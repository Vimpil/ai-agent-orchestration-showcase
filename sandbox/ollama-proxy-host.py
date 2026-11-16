#!/usr/bin/env python3
"""Phase4 Ollama HTTP allowlist proxy (host side, Unix socket -> 127.0.0.1:11434).
Only forwards inference endpoints; blocks model-management.
"""
import socket, os, sys, urllib.parse, posixpath, threading, http.client, json

ALLOWED = {
    ('GET', '/v1/models'),
    ('GET', '/api/tags'),
    ('GET', '/api/version'),
    ('POST', '/v1/chat/completions'),
    ('POST', '/api/show'),
}
# also allow GET /v1/models/<name> (model detail) — prefix check
def normalized_path(raw: str) -> str:
    # raw is path with possible query and %encoding
    p = urllib.parse.urlsplit(raw).path
    p = urllib.parse.unquote(p)
    # collapse // and . / .. without escaping root
    # posixpath.normpath on /v1/../api/delete -> /api/delete (blocked correctly)
    if p == "":
        p = "/"
    # ensure leading /
    if not p.startswith("/"):
        p = "/" + p
    n = posixpath.normpath(p)
    # trailing slash: normpath strips; re-add for /v1/models/ should still match /v1/models
    return n

def is_allowed(method: str, raw_path: str) -> bool:
    method = method.upper()
    p = normalized_path(raw_path)
    if (method, p) in ALLOWED:
        return True
    # allow GET /v1/models/<id> (single segment, no .. after norm)
    if method == "GET" and p.startswith("/v1/models/"):
        rest = p[len("/v1/models/"):]
        if rest and "/" not in rest:
            return True
    return False

def handle_client(conn: socket.socket, log_f):
    try:
        conn.settimeout(30)
        f = conn.makefile('rwb', buffering=0)
        for _ in range(100):  # keep-alive loop
            # read request line
            line = f.readline(8192)
            if not line:
                break
            try:
                line_s = line.decode('iso-8859-1').strip()
            except Exception:
                break
            if not line_s:
                continue
            parts = line_s.split()
            if len(parts) < 2:
                resp = b"HTTP/1.1 400 Bad Request\r\nContent-Length: 0\r\nConnection: close\r\n\r\n"
                f.write(resp)
                break
            method, raw_path = parts[0], parts[1]
            # read headers
            headers = {}
            hdr_list = []
            while True:
                hl = f.readline(8192)
                if not hl or hl in (b"\r\n", b"\n"):
                    break
                try:
                    s = hl.decode('iso-8859-1').strip()
                except Exception:
                    s = ""
                hdr_list.append(s)
                if ":" in s:
                    k, v = s.split(":", 1)
                    headers[k.strip().lower()] = v.strip()
            # read body (Content-Length or chunked)
            body = b""
            if "transfer-encoding" in headers and "chunked" in headers["transfer-encoding"].lower():
                # dechunk
                chunks = []
                while True:
                    cl = f.readline(8192)
                    if not cl:
                        break
                    try:
                        size = int(cl.strip().split(b";")[0], 16)
                    except Exception:
                        break
                    if size == 0:
                        # read trailers until empty line
                        while True:
                            tl = f.readline(8192)
                            if not tl or tl in (b"\r\n", b"\n"):
                                break
                        break
                    data = f.read(size)
                    chunks.append(data)
                    f.read(2)
                    if len(b"".join(chunks)) > 20*1024*1024:
                        body = None
                        break
                if body is not None:
                    body = b"".join(chunks)
            elif "content-length" in headers:
                try:
                    ln = int(headers["content-length"])
                except Exception:
                    ln = 0
                if ln > 20*1024*1024:
                    body = None
                else:
                    body = f.read(ln) if ln else b""
            # log first line
            try:
                log_f.write(f"OLLAMA {method} {raw_path} allowed={is_allowed(method, raw_path)}\n")
                log_f.flush()
            except Exception:
                pass
            if body is None:
                resp = b"HTTP/1.1 413 Payload Too Large\r\nContent-Length: 0\r\nConnection: close\r\n\r\n"
                f.write(resp)
                break
            if not is_allowed(method, raw_path):
                payload = json.dumps({"error": "sandbox: ollama endpoint blocked"}).encode()
                resp = (b"HTTP/1.1 403 Forbidden\r\nContent-Type: application/json\r\nContent-Length: " + str(len(payload)).encode() + b"\r\nConnection: close\r\n\r\n" + payload)
                f.write(resp)
                # close after block (avoid reuse confusion)
                break
            # forward to host Ollama
            try:
                oc = http.client.HTTPConnection("127.0.0.1", 11434, timeout=120)
                # rebuild headers without hop-by-hop
                fw_headers = {}
                for k, v in headers.items():
                    if k.lower() in ("host", "connection", "content-length", "transfer-encoding"):
                        continue
                    fw_headers[k] = v
                # http.client will set Host/Content-Length automatically
                oc.request(method, raw_path, body=body if body else None, headers=fw_headers)
                resp_obj = oc.getresponse()
                # stream response headers
                rh = {k: v for k, v in resp_obj.getheaders() if k.lower() not in ("transfer-encoding",)}
                # Need to decide framing: Ollama may use chunked or length. http.client handles.
                # Forward as HTTP/1.1 with Content-Length if available, else chunked streaming with close.
                # Simpler: use resp_obj.length if present, else stream chunked.
                status = resp_obj.status
                reason = resp_obj.reason or ""
                f.write(f"HTTP/1.1 {status} {reason}\r\n".encode())
                for k, v in rh.items():
                    f.write(f"{k}: {v}\r\n".encode())
                length = resp_obj.length
                if length is not None:
                    f.write(b"\r\n")
                    while True:
                        chunk = resp_obj.read(8192)
                        if not chunk:
                            break
                        f.write(chunk)
                else:
                    # chunked stream (SSE) — forward as chunked
                    f.write(b"Transfer-Encoding: chunked\r\n\r\n")
                    while True:
                        chunk = resp_obj.read1(8192) if hasattr(resp_obj, 'read1') else resp_obj.read(8192)
                        if not chunk:
                            break
                        f.write(f"{len(chunk):X}\r\n".encode() + chunk + b"\r\n")
                    f.write(b"0\r\n\r\n")
                oc.close()
            except Exception as e:
                try:
                    f.write(b"HTTP/1.1 502 Bad Gateway\r\nContent-Length: 0\r\nConnection: close\r\n\r\n")
                except Exception:
                    pass
                break
            # keep-alive: if client requested close, break
            if headers.get("connection", "").lower() == "close":
                break
    except Exception:
        pass
    finally:
        try:
            conn.close()
        except Exception:
            pass

def main():
    sock_path = sys.argv[1] if len(sys.argv) > 1 else "/tmp/ollama.sock"
    log_path = sys.argv[2] if len(sys.argv) > 2 else "/tmp/ollama-proxy.log"
    os.makedirs(os.path.dirname(sock_path), exist_ok=True)
    try:
        os.unlink(sock_path)
    except FileNotFoundError:
        pass
    srv = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    srv.bind(sock_path)
    srv.listen(50)
    try:
        os.chmod(sock_path, 0o777)
    except Exception:
        pass
    log_f = open(log_path, 'a')
    while True:
        c, _ = srv.accept()
        t = threading.Thread(target=handle_client, args=(c, log_f), daemon=True)
        t.start()

if __name__ == '__main__':
    main()
