from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

from .platforming import is_windows, run_checked


def setup_linux_user(user: str, target: str, repo: Path, apply: bool) -> None:
    if is_windows():
        raise SystemExit("linux-user setup is only available on Linux.")
    target_path = Path(target).expanduser().resolve()
    commands = _commands(user, target_path, repo.resolve())
    if not apply:
        print("Dry run. Re-run with --apply to execute:")
        for cmd in commands:
            print("  " + " ".join(cmd))
        return
    if os.geteuid() != 0:
        raise SystemExit("Run linux-user setup with sudo when using --apply.")
    if not _user_exists(user):
        run_checked(["useradd", "--system", "--create-home", "--shell", "/bin/bash", user])
    target_path.mkdir(parents=True, exist_ok=True)
    _copy_repo(repo.resolve(), target_path)
    _chown_tree(target_path, user)
    print(f"Prepared {target_path} for user {user}")


def _commands(user: str, target: Path, repo: Path) -> list[list[str]]:
    cmds: list[list[str]] = []
    if not _user_exists(user):
        cmds.append(["useradd", "--system", "--create-home", "--shell", "/bin/bash", user])
    cmds.extend(
        [
            ["mkdir", "-p", str(target)],
            ["copy", str(repo), str(target), "excluding .git deployments profiles __pycache__"],
            ["chown", "-R", f"{user}:{user}", str(target)],
        ]
    )
    return cmds


def _user_exists(user: str) -> bool:
    if shutil.which("id") is None:
        return False
    return subprocess.run(["id", "-u", user], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False).returncode == 0


def _copy_repo(repo: Path, target: Path) -> None:
    ignored = {".git", "deployments", "profiles", "__pycache__"}
    for item in repo.iterdir():
        if item.name in ignored:
            continue
        dest = target / item.name
        if item.is_dir():
            shutil.copytree(item, dest, dirs_exist_ok=True, ignore=shutil.ignore_patterns("__pycache__"))
        else:
            shutil.copy2(item, dest)


def _chown_tree(target: Path, user: str) -> None:
    import grp
    import pwd

    uid = pwd.getpwnam(user).pw_uid
    gid = grp.getgrnam(user).gr_gid
    for root, dirs, files in os.walk(target):
        os.chown(root, uid, gid)
        for name in dirs + files:
            os.chown(Path(root) / name, uid, gid)
