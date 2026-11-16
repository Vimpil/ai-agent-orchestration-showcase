#!/usr/bin/env python3
"""Phase4 git client shim (inside sandbox, ro-bind at /usr/bin/git and /bin/git).
Forwards argv to host proxy via /sandbox-state/git.sock, prints output, exits rc.
No real git binary exists inside the sandbox.
"""
import socket, sys, json
def main():
    argv = sys.argv[1:]
    try:
        s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        s.settimeout(70)
        s.connect("/sandbox-state/git.sock")
        req = json.dumps({"argv": argv}).encode() + b"\n"
        s.sendall(req)
        f = s.makefile('rb', buffering=0)
        line = f.readline(10*1024*1024)
        s.close()
        if not line:
            sys.stderr.write("sandbox: git proxy unavailable\n")
            sys.exit(1)
        resp = json.loads(line.decode())
        out = resp.get("stdout", "") or ""
        err = resp.get("stderr", "") or ""
        rc = int(resp.get("rc", 1))
        if out:
            sys.stdout.write(out)
        if err:
            sys.stderr.write(err)
        sys.exit(rc)
    except FileNotFoundError:
        sys.stderr.write("sandbox: git proxy unavailable\n")
        sys.exit(1)
    except Exception as e:
        sys.stderr.write(f"sandbox: git proxy error: {e}\n")
        sys.exit(1)
if __name__ == '__main__':
    main()
