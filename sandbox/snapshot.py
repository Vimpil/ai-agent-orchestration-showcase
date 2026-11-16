#!/usr/bin/env python3
"""Phase4 snapshot + export. Host side only (outside sandbox)."""
import os, sys, json, hashlib, shutil, re
from pathlib import Path

SECRET_BASENAMES_CASEFOLD = {
    '.env', '.envrc', '.npmrc', '.pypirc', '.netrc', 'authorized_keys', 'known_hosts',
    'credentials.json', 'secrets.json', 'api_key.json', 'token.json', 'config.json',
    'id_rsa', 'id_rsa.pub', 'id_ed25519', 'id_ed25519.pub', 'id_ecdsa', 'id_ecdsa.pub',
    'id_dsa', 'id_dsa.pub',
}
SECRET_SUFFIXES = ('.pem', '.key', '.p12', '.pfx', '.gpg', '.asc', '.env', '.credentials', '.log')
# substrings (case-insensitive) in basename
SECRET_SUBSTR = ('credentials', 'secret', 'token', 'api_key', 'api-key', 'apikey')
EXCLUDE_DIRS_TOP = {'.ssh', '.gnupg', '.aws', '.kube'}
# bare-repo dirs named *.git (except .git itself) are excluded from snapshot+export
def is_secret_file(rel: str, name: str) -> bool:
    low = name.lower()
    parts = low.split('/')
    # any component is .ssh etc?
    if any(p in EXCLUDE_DIRS_TOP for p in Path(rel).parts):
        return True
    if low in SECRET_BASENAMES_CASEFOLD:
        return True
    # .env.* (e.g. .env.local .env.prod) except allowlisted .env.example
    if low.startswith('.env.') and not low.endswith('.env.example'):
        return True
    for suf in SECRET_SUFFIXES:
        if low.endswith(suf):
            # .env.example is allowlisted (not secret)
            if low.endswith('.env.example'):
                return False
            return True
    for sub in SECRET_SUBSTR:
        if sub in low:
            return True
    # id_* generic keys (e.g. id_foo, id_custom) without extension
    if low.startswith('id_'):
        return True
    return False

def is_bare_rel(rel: str) -> bool:
    # True if any component ends with .git and is not exactly .git at top
    for p in Path(rel).parts:
        if p.endswith('.git') and p != '.git':
            return True
    return False

def file_hash(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for chunk in iter(lambda: f.read(65536), b''):
            h.update(chunk)
    return h.hexdigest()

def sanitize_git_config(snap_git_config: Path):
    """Redact credentials in remote URLs. Returns True if changed."""
    try:
        text = snap_git_config.read_text(errors='ignore')
    except Exception:
        return False
    # Replace ://user:pass@ with ://user@
    new = re.sub(r'(://[^:/@\s]+):[^/\s@]+@', r'\1@', text)
    # Also redact password in ssh? leave.
    if new != text:
        snap_git_config.write_text(new)
        return True
    return False

def write_manifest_safely(path: Path, text: str):
    """Write manifest without following a symlink (R6A-02b).

    Uses O_NOFOLLOW so a pre-planted or dangling symlink fails closed
    (ELOOP/ValueError) instead of truncating its target outside RUN_ROOT.
    Absent -> exclusive create (O_CREAT|O_EXCL|O_NOFOLLOW, 0644); existing
    -> require regular file owned by invoking uid, then O_NOFOLLOW|O_TRUNC.
    Parent RUN_ROOT is validated by the wrapper (700, invoking uid, no
    symlink components). Residual validate-to-use race remains (same-UID
    swap between lstat and open); O_NOFOLLOW prevents the follow turning
    into an outside write, but does not anchor the path to a dirfd.
    Format is identical to Path.write_text (utf-8, no added newline).
    """
    import stat as _stat
    try:
        st = os.lstat(path)
    except FileNotFoundError:
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o644)
    else:
        if _stat.S_ISLNK(st.st_mode) or not _stat.S_ISREG(st.st_mode):
            raise ValueError(f"refusing manifest symlink/non-regular: {path}")
        if st.st_uid != os.getuid():
            raise ValueError(f"refusing manifest not owned by invoking uid: {path}")
        fd = os.open(path, os.O_WRONLY | os.O_NOFOLLOW | os.O_TRUNC)
    try:
        os.write(fd, text.encode("utf-8"))
    finally:
        os.close(fd)

def create_snapshot(src: Path, dst: Path, manifest_path: Path, log_path: Path):
    src = src.resolve()
    dst.mkdir(parents=True, exist_ok=True)
    log = open(log_path, 'a')
    def L(s):
        print(s, file=log); print(s)
    manifest = {'src': str(src), 'files': {}, 'dirs': [], 'sanitized_config': False, 'excluded': []}
    # Walk src excluding .git handled separately? Include .git (sanitized) for history.
    for root, dirs, files in os.walk(src, topdown=True, followlinks=False):
        root_p = Path(root)
        rel_root = root_p.relative_to(src)
        # prune excluded dirs (do not descend)
        # dirs list is mutable
        pruned = []
        for d in list(dirs):
            # d is name
            rel_dir = (rel_root / d) if str(rel_root) != '.' else Path(d)
            # bare repo dir?
            if (rel_dir.name.endswith('.git') and rel_dir.name != '.git'):
                L(f"snapshot: exclude bare {rel_dir}")
                manifest['excluded'].append(str(rel_dir))
                pruned.append(d)
                continue
            if d in EXCLUDE_DIRS_TOP:
                L(f"snapshot: exclude secret-dir {rel_dir}")
                manifest['excluded'].append(str(rel_dir))
                pruned.append(d)
                continue
            dst_dir = dst / rel_dir
            try:
                # create dir if not exists and not symlink
                if os.path.islink(root_p / d):
                    # symlink to dir: do not descend (os.walk won't follow)
                    pass
                else:
                    dst_dir.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                L(f"snapshot: mkdir fail {rel_dir}: {e}")
        for d in pruned:
            dirs.remove(d)
        # files (including symlinks listed in files by os.walk? symlinks to files appear in files)
        for name in files:
            src_file = root_p / name
            rel = (rel_root / name) if str(rel_root) != '.' else Path(name)
            # bare inside file path?
            if is_bare_rel(str(rel)):
                L(f"snapshot: exclude bare-file {rel}")
                manifest['excluded'].append(str(rel))
                continue
            if is_secret_file(str(rel), name):
                # allow .env.example
                if name.lower().endswith('.env.example'):
                    pass
                else:
                    L(f"snapshot: exclude secret {rel}")
                    manifest['excluded'].append(str(rel))
                    continue
            # handle symlink
            dst_file = dst / rel
            try:
                st = os.lstat(src_file)
            except Exception as e:
                L(f"snapshot: lstat fail {rel}: {e}")
                continue
            import stat
            if stat.S_ISLNK(st.st_mode):
                target = os.readlink(src_file)
                try:
                    if dst_file.exists() or os.path.islink(dst_file):
                        dst_file.unlink()
                    os.symlink(target, dst_file)
                    manifest['files'][str(rel)] = {'type': 'symlink', 'target': target}
                    L(f"snapshot: symlink {rel} -> {target}")
                except Exception as e:
                    L(f"snapshot: symlink fail {rel}: {e}")
                continue
            if not stat.S_ISREG(st.st_mode):
                L(f"snapshot: skip non-regular {rel}")
                manifest['excluded'].append(str(rel))
                continue
            if st.st_nlink > 1:
                L(f"snapshot: exclude hardlink {rel} nlink={st.st_nlink}")
                manifest['excluded'].append(str(rel))
                continue
            # regular file: copy (breaks any hardlink because new inode)
            try:
                dst_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src_file, dst_file, follow_symlinks=False)
                h = file_hash(dst_file)
                manifest['files'][str(rel)] = {'type': 'file', 'hash': h, 'size': dst_file.stat().st_size}
            except Exception as e:
                L(f"snapshot: copy fail {rel}: {e}")
                manifest['excluded'].append(str(rel))
    # sanitize .git/config in snapshot (not src)
    cfg = dst / '.git' / 'config'
    if cfg.exists() and not os.path.islink(cfg):
        if sanitize_git_config(cfg):
            manifest['sanitized_config'] = True
            L("snapshot: sanitized .git/config credentials")
    write_manifest_safely(manifest_path, json.dumps(manifest, indent=2))
    L(f"snapshot: done files={len(manifest['files'])} excluded={len(manifest['excluded'])}")
    log.close()

def export_snapshot(snap: Path, src: Path, manifest_path: Path, log_path: Path):
    manifest = json.loads(manifest_path.read_text())
    init_files = manifest.get('files', {})
    log = open(log_path, 'a')
    def L(s):
        print(s, file=log); print(s)
    exported, skipped, blocked = [], [], []
    # Walk snapshot files
    for root, dirs, files in os.walk(snap, topdown=True, followlinks=False):
        root_p = Path(root)
        rel_root = root_p.relative_to(snap)
        # do not export .git at all (protect hooks/config/refs)
        if '.git' in dirs:
            # still need to prune .git from export walk, but log
            dirs.remove('.git')
            L("export: skip .git (hooks/config/refs protected)")
        # prune bare dirs
        for d in list(dirs):
            rel_dir = (rel_root / d) if str(rel_root) != '.' else Path(d)
            if rel_dir.name.endswith('.git') and rel_dir.name != '.git':
                dirs.remove(d)
                L(f"export: skip bare {rel_dir}")
        for name in files:
            snap_file = root_p / name
            rel = (rel_root / name) if str(rel_root) != '.' else Path(name)
            rel_s = str(rel)
            # block secret-pattern new files from export
            if is_secret_file(rel_s, name) and not name.lower().endswith('.env.example'):
                L(f"export: BLOCK secret-pattern {rel_s}")
                blocked.append(rel_s)
                continue
            src_file = src / rel
            try:
                st = os.lstat(snap_file)
            except Exception:
                continue
            import stat
            # symlink handling: only export if target stays inside project (relative)
            if stat.S_ISLNK(st.st_mode):
                target = os.readlink(snap_file)
                # Absolute or ../ escaping = block
                if os.path.isabs(target):
                    L(f"export: BLOCK absolute symlink {rel_s} -> {target}")
                    blocked.append(rel_s)
                    continue
                # Resolve relative to src parent
                resolved = (src_file.parent / target).resolve()
                # Must be inside src
                try:
                    resolved.relative_to(src.resolve())
                except ValueError:
                    L(f"export: BLOCK escaping symlink {rel_s} -> {target}")
                    blocked.append(rel_s)
                    continue
                # Only export if symlink is new/changed (compare to manifest)
                init = init_files.get(rel_s)
                if init and init.get('type') == 'symlink' and init.get('target') == target:
                    skipped.append(rel_s)
                    continue
                # Export symlink
                try:
                    src_file.parent.mkdir(parents=True, exist_ok=True)
                    if os.path.islink(src_file) or src_file.exists():
                        if os.path.islink(src_file):
                            src_file.unlink()
                        elif src_file.is_dir():
                            L(f"export: skip symlink over dir {rel_s}")
                            skipped.append(rel_s)
                            continue
                        else:
                            src_file.unlink()
                    os.symlink(target, src_file)
                    exported.append(rel_s)
                    L(f"export: symlink {rel_s}")
                except Exception as e:
                    L(f"export: symlink fail {rel_s}: {e}")
                    skipped.append(rel_s)
                continue
            if not stat.S_ISREG(st.st_mode):
                continue
            # hardlink check in snapshot: if agent created hardlink with nlink>1, do not export (break link by copying? safer to skip)
            if st.st_nlink > 1:
                L(f"export: BLOCK hardlink {rel_s} nlink={st.st_nlink}")
                blocked.append(rel_s)
                continue
            # new or changed?
            try:
                snap_hash = file_hash(snap_file)
            except Exception:
                continue
            init = init_files.get(rel_s)
            # If unchanged since snapshot and host unchanged, skip
            if init and init.get('type') == 'file' and init.get('hash') == snap_hash:
                # unchanged working tree file: ensure host still exists (no export needed)
                skipped.append(rel_s)
                continue
            # If file is new in snapshot (not in init), or changed:
            # Check host not changed since initial (if init existed)
            if init and init.get('type') == 'file':
                # init hash is initial content hash
                if src_file.exists() and not os.path.islink(src_file) and src_file.is_file():
                    try:
                        host_hash = file_hash(src_file)
                    except Exception:
                        host_hash = None
                    if host_hash is not None and host_hash != init['hash']:
                        L(f"export: CONFLICT host-changed, skip {rel_s}")
                        skipped.append(rel_s)
                        continue
                elif src_file.exists() or os.path.islink(src_file):
                    # type changed on host (now symlink/dir) -> skip
                    L(f"export: CONFLICT type-change, skip {rel_s}")
                    skipped.append(rel_s)
                    continue
                # else host deleted since initial -> do not resurrect? skip (log)
                if not src_file.exists() and not os.path.islink(src_file):
                    L(f"export: host-deleted, skip resurrect {rel_s}")
                    skipped.append(rel_s)
                    continue
            # new file in snapshot that doesn't exist on host: export (create)
            # changed file: export
            try:
                src_file.parent.mkdir(parents=True, exist_ok=True)
                # if src is symlink, remove first
                if os.path.islink(src_file):
                    src_file.unlink()
                shutil.copy2(snap_file, src_file, follow_symlinks=False)
                exported.append(rel_s)
                L(f"export: file {rel_s}")
            except Exception as e:
                L(f"export: copy fail {rel_s}: {e}")
                skipped.append(rel_s)
    # deletions: do not auto-delete host files; log
    # Find init files missing in snapshot
    for rel_s, meta in init_files.items():
        if meta.get('type') == 'file' and not (snap / rel_s).exists() and not os.path.islink(snap / rel_s):
            L(f"export: snapshot-deleted {rel_s} (host NOT deleted, needs review)")
    L(f"export: done exported={exported} skipped={len(skipped)} blocked={blocked}")
    log.close()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("usage: snapshot.py create|export ...", file=sys.stderr); sys.exit(2)
    cmd = sys.argv[1]
    if cmd == 'create':
        # snapshot.py create SRC DST MANIFEST LOG
        create_snapshot(Path(sys.argv[2]), Path(sys.argv[3]), Path(sys.argv[4]), Path(sys.argv[5]))
    elif cmd == 'export':
        export_snapshot(Path(sys.argv[2]), Path(sys.argv[3]), Path(sys.argv[4]), Path(sys.argv[5]))
    else:
        print(f"unknown {cmd}", file=sys.stderr); sys.exit(2)
