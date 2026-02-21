from __future__ import annotations
from pathlib import Path
import os
import subprocess
import yaml
from repo_mesh.contracts import RepoRegistration


def assert_github_auth_present() -> None:
    if os.getenv("GITHUB_TOKEN"):
        return
    result = subprocess.run(
        ["gh", "auth", "status"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError("GitHub auth missing. Set GITHUB_TOKEN or run: gh auth login")


def load_selected_repos(repos_yaml: str) -> list[RepoRegistration]:
    payload = yaml.safe_load(Path(repos_yaml).read_text(encoding="utf-8"))
    selected: list[RepoRegistration] = []
    for raw in payload.get("repos", []):
        if not raw.get("selected", False):
            continue
        repo = RepoRegistration(**raw)
        if not repo.read_only:
            raise ValueError(f"Repo {repo.repo_id} must be read_only=True")
        if not Path(repo.local_path).exists():
            raise FileNotFoundError(f"Missing local repo checkout: {repo.local_path}")
        selected.append(repo)
    return selected
