#!/usr/bin/env python3
"""Phase4 Git host proxy: Unix socket -> allowlisted git on snapshot (host side).
Listens on git.sock, receives JSON {argv:[...]}, runs git -C SNAPSHOT with sanitized env.
"""
import socket, os, sys, json, subprocess, threading

ALLOWED = {"status","diff","log","show","branch","add","commit","checkout","switch","rev-parse","ls-files","describe","diff-tree","diff-index","diff-files"}
# Control opts that must be rejected as first arg or inside argv
FORBIDDEN_OPTS = {"-c","-C","--git-dir","--work-tree","--exec-path","--config-env","--literal-pathspecs"}
FORBIDDEN_SUB = {"push","pull","fetch","clone","remote","submodule","worktree","reset","clean","restore","stash","rebase","merge","cherry-pick","am","apply","bisect","ls-remote","archive","bundle","push","config","credential","send-email","request-pull","instaweb","web--browse"}

def validate(argv):
    if not argv:
        return (False, "empty", 1, "", "sandbox: git requires a subcommand\n")
    # help/version at top level
    if argv[0] in ("--version","version"):
        return (True, "version", 0, None, None)  # special
    if argv[0] in ("--help","help","-h","--h"):
        return (True, "help", 0, None, None)
    if argv[0].startswith("-"):
        return (False, "opt", 1, "", f"sandbox: git option blocked: {argv[0]}\n")
    sub = argv[0]
    if sub not in ALLOWED:
        return (False, sub, 1, "", f"sandbox: git {sub} is blocked\n")
    # reject dangerous opts anywhere in argv
    for a in argv:
        if a in FORBIDDEN_OPTS or a.startswith("--git-dir") or a.startswith("--work-tree") or a.startswith("--exec-path"):
            return (False, sub, 1, "", f"sandbox: git option blocked: {a}\n")
        if a == "-c":
            return (False, sub, 1, "", "sandbox: git -c is blocked\n")
        # block --output=, --upload-pack, --receive-pack, etc. that could write/publish
        if a.startswith("--output") or a.startswith("--upload-pack") or a.startswith("--receive-pack") or a.startswith("--push") or a.startswith("--force") and sub not in ALLOWED:
            # --force is only relevant to push, which is already blocked; but be strict: block --force for branch? branch -f (force-create) has -f, not --force. Allow -f for branch? We'll block only --force as opt.
            return (False, sub, 1, "", f"sandbox: git option blocked: {a}\n")
        # block -p / --paginate? not needed
        if a in ("-p","--paginate") or a.startswith("--paginate"):
            return (False, sub, 1, "", f"sandbox: git option blocked: {a}\n")
    # block pathspec absolute outside repo? git itself will error, but reject obvious outside paths starting with / and containing ..
    return (True, sub, None, None, None)

def run_git(snapshot: str, argv):
    ok, sub, rc, out, err = validate(argv)
    if not ok:
        return {"rc": rc, "stdout": out or "", "stderr": err or ""}
    if sub == "version":
        try:
            r = subprocess.run(["/usr/bin/git","--version"], capture_output=True, text=True, timeout=10)
            return {"rc": r.returncode, "stdout": r.stdout, "stderr": r.stderr}
        except Exception as e:
            return {"rc": 1, "stdout": "", "stderr": str(e)}
    if sub == "help":
        try:
            r = subprocess.run(["/usr/bin/git","--help"], capture_output=True, text=True, timeout=10)
            return {"rc": 0, "stdout": r.stdout[:4000], "stderr": r.stderr}
        except Exception as e:
            return {"rc": 1, "stdout": "", "stderr": str(e)}
    # sanitized env: minimal, no GIT_CONFIG_* injection, no GIT_DIR, etc.
    clean_env = {
        "PATH": "/usr/bin:/bin:/usr/sbin:/sbin",
        "HOME": "/nonexistent",
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_CONFIG_GLOBAL": "/dev/null",
        "GIT_CONFIG_SYSTEM": "/dev/null",
        "GIT_TERMINAL_PROMPT": "0",
        "GIT_SSH_COMMAND": "false",
        "SSH_ASKPASS": "/bin/false",
        "GIT_ASKPASS": "/bin/false",
        "GIT_PAGER": "cat",
        "PAGER": "cat",
        "LC_ALL": "C.UTF-8",
    }
    # harden vs hooks/fsmonitor: -c core.hooksPath=/dev/null etc. must come before subcommand
    cmd = ["/usr/bin/git", "-c", "core.hooksPath=/dev/null", "-c", "core.fsmonitor=", "-c", "core.pager=cat", "-C", snapshot] + argv
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=60, env=clean_env)
        return {"rc": r.returncode, "stdout": r.stdout, "stderr": r.stderr}
    except Exception as e:
        return {"rc": 1, "stdout": "", "stderr": f"sandbox: git proxy error: {e}\n"}

def handle(conn, snapshot, log_f):
    try:
        conn.settimeout(70)
        f = conn.makefile('rwb', buffering=0)
        line = f.readline(1024*1024)
        if not line:
            return
        try:
            req = json.loads(line.decode())
            argv = req.get("argv", [])
            if not isinstance(argv, list):
                raise ValueError("argv not list")
            argv = [str(x) for x in argv]
        except Exception:
            resp = {"rc": 1, "stdout": "", "stderr": "sandbox: git proxy bad request\n"}
            f.write((json.dumps(resp)+"\n").encode())
            return
        res = run_git(snapshot, argv)
        try:
            log_f.write(f"GIT {argv!r} -> rc={res.get('rc')}\n")
            log_f.flush()
        except Exception:
            pass
        f.write((json.dumps(res)+"\n").encode())
    except Exception:
        pass
    finally:
        try:
            conn.close()
        except Exception:
            pass

def main():
    sock_path = sys.argv[1]
    snapshot = sys.argv[2]
    log_path = sys.argv[3] if len(sys.argv) > 3 else "/tmp/git-proxy.log"
    os.makedirs(os.path.dirname(sock_path), exist_ok=True)
    try:
        os.unlink(sock_path)
    except FileNotFoundError:
        pass
    srv = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    srv.bind(sock_path)
    srv.listen(20)
    try:
        os.chmod(sock_path, 0o777)
    except Exception:
        pass
    log_f = open(log_path, 'a')
    while True:
        c, _ = srv.accept()
        t = threading.Thread(target=handle, args=(c, snapshot, log_f), daemon=True)
        t.start()

if __name__ == '__main__':
    main()
