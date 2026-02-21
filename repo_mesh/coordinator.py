from __future__ import annotations
import json
from pathlib import Path
from repo_mesh.discussion import synthesize_profiles
from repo_mesh.evidence import extract_repo_evidence
from repo_mesh.profile import build_repo_profile
from repo_mesh.repo_loader import load_selected_repos


def run_once(repos_yaml: str, out_json: str) -> None:
    repos = load_selected_repos(repos_yaml)
    profiles = []
    for repo in repos:
        evidence = extract_repo_evidence(repo.repo_id, repo.local_path)
        profiles.append(build_repo_profile(repo.repo_id, evidence))

    consensus = synthesize_profiles(profiles)
    payload = {
        "repo_count": len(profiles),
        "profiles": [p.__dict__ for p in profiles],
        "consensus": consensus,
    }
    Path(out_json).parent.mkdir(parents=True, exist_ok=True)
    Path(out_json).write_text(json.dumps(payload, indent=2), encoding="utf-8")
