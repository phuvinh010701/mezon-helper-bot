"""Host images on this repo: commit + push, return the raw.githubusercontent URL."""

import os
import subprocess
from pathlib import Path


def _git(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *args], check=False, text=True)


def publish_image(path: Path) -> str:
    """Push `path` to the current branch and return its public URL (GitHub Actions only)."""
    repo, branch = os.environ["GITHUB_REPOSITORY"], os.environ["GITHUB_REF_NAME"]
    _git("config", "user.name", "github-actions")
    _git("config", "user.email", "github-actions@users.noreply.github.com")
    _git("add", str(path))
    if _git("diff", "--cached", "--quiet").returncode:  # something staged
        subprocess.run(["git", "commit", "-m", f"asset: {path}"], check=True)
        subprocess.run(["git", "pull", "--rebase", "origin", branch], check=True)
        subprocess.run(["git", "push", "origin", branch], check=True)
    return f"https://raw.githubusercontent.com/{repo}/{branch}/{path.as_posix()}"
