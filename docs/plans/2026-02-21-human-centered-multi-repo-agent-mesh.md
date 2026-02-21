# Human-Centered Multi-Repo Agent Mesh Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build an on-demand local, read-only multi-agent system where one agent owns one repository, infers human-centered signals (skills, intentions, interests), and then participates in cross-repo discussion to produce a unified user profile.

**Architecture:** Implement a hub-and-spoke design: `RepoOwnerAgent` workers extract evidence per repo, then a `Coordinator` mediates discussion and consensus across repo agents. Keep repository access read-only by policy, allow code reading for inference, and persist only structured findings plus evidence references. Start with Codex-backed prompts and leave model adapters pluggable for future Claude/Gemini integration.

**Tech Stack:** Python 3.11, pytest, PyYAML, dataclasses, pathlib, subprocess

**Execution standards:** Follow @superpowers:test-driven-development, @superpowers:verification-before-completion, and @superpowers:requesting-code-review during implementation.

---

### Task 1: Scaffold Contracts and Config

**Files:**
- Create: `repo_mesh/__init__.py`
- Create: `repo_mesh/contracts.py`
- Create: `repo_mesh/config/repos.yaml`
- Create: `repo_mesh/config/policy.yaml`
- Create: `repo_mesh/output/.gitkeep`
- Create: `tests/repo_mesh/test_contracts.py`

**Step 1: Write the failing test**

```python
# tests/repo_mesh/test_contracts.py
from pathlib import Path
import yaml


def test_contract_config_files_exist_and_read_only_default():
    repos_path = Path("repo_mesh/config/repos.yaml")
    policy_path = Path("repo_mesh/config/policy.yaml")
    assert repos_path.exists()
    assert policy_path.exists()

    repos = yaml.safe_load(repos_path.read_text(encoding="utf-8"))
    policy = yaml.safe_load(policy_path.read_text(encoding="utf-8"))
    assert isinstance(repos["repos"], list)
    assert policy["repo_access_mode"] == "read_only"
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/repo_mesh/test_contracts.py -v`  
Expected: FAIL with missing files.

**Step 3: Write minimal implementation**

```python
# repo_mesh/contracts.py
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List


@dataclass(frozen=True)
class RepoRegistration:
    repo_id: str
    display_name: str
    github_full_name: str
    local_path: str
    selected: bool = True
    read_only: bool = True


@dataclass(frozen=True)
class AgentPolicy:
    repo_access_mode: str = "read_only"
    cross_repo_share_mode: str = "derived_only"
    allow_code_read: bool = True
    max_shared_snippets_per_turn: int = 0


@dataclass(frozen=True)
class EvidenceItem:
    evidence_id: str
    repo_id: str
    signal_type: str
    summary: str
    source_ref: str
    weight: float = 1.0


@dataclass(frozen=True)
class RepoProfile:
    repo_id: str
    skills: List[str] = field(default_factory=list)
    intentions: List[str] = field(default_factory=list)
    interests: List[str] = field(default_factory=list)
    evidence_ids: List[str] = field(default_factory=list)
```

```yaml
# repo_mesh/config/repos.yaml
repos:
  - repo_id: "knowme-core"
    display_name: "KnowMe Core"
    github_full_name: "your-org/knowme-core"
    local_path: "./workspace/knowme-core"
    selected: true
    read_only: true
  - repo_id: "knowme-ui"
    display_name: "KnowMe UI"
    github_full_name: "your-org/knowme-ui"
    local_path: "./workspace/knowme-ui"
    selected: false
    read_only: true
```

```yaml
# repo_mesh/config/policy.yaml
repo_access_mode: "read_only"
cross_repo_share_mode: "derived_only"
allow_code_read: true
max_shared_snippets_per_turn: 0
```

```python
# repo_mesh/__init__.py
"""Human-centered multi-repo agent mesh."""
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/repo_mesh/test_contracts.py -v`  
Expected: PASS

**Step 5: Commit**

```bash
git add repo_mesh tests/repo_mesh/test_contracts.py
git commit -m "chore: scaffold repo mesh contracts and config"
```

### Task 2: Implement GitHub/Repo Access Preflight and Selection Loader

**Files:**
- Create: `repo_mesh/repo_loader.py`
- Create: `tests/repo_mesh/test_repo_loader.py`
- Modify: `repo_mesh/contracts.py`

**Step 1: Write the failing test**

```python
# tests/repo_mesh/test_repo_loader.py
from pathlib import Path
import yaml


def test_load_selected_repos_returns_only_selected_and_read_only(tmp_path):
    from repo_mesh.repo_loader import load_selected_repos

    cfg = tmp_path / "repos.yaml"
    cfg.write_text(
        yaml.safe_dump(
            {
                "repos": [
                    {
                        "repo_id": "a",
                        "display_name": "A",
                        "github_full_name": "org/a",
                        "local_path": str(tmp_path / "a"),
                        "selected": True,
                        "read_only": True,
                    },
                    {
                        "repo_id": "b",
                        "display_name": "B",
                        "github_full_name": "org/b",
                        "local_path": str(tmp_path / "b"),
                        "selected": False,
                        "read_only": True,
                    },
                ]
            }
        ),
        encoding="utf-8",
    )
    (tmp_path / "a").mkdir()
    (tmp_path / "b").mkdir()

    repos = load_selected_repos(str(cfg))
    assert [r.repo_id for r in repos] == ["a"]
    assert repos[0].read_only is True
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/repo_mesh/test_repo_loader.py -v`  
Expected: FAIL with import/module not found.

**Step 3: Write minimal implementation**

```python
# repo_mesh/repo_loader.py
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
```

```python
# repo_mesh/contracts.py (append)
@dataclass(frozen=True)
class AgentRunContext:
    run_id: str
    repos_yaml: str
    policy_yaml: str
    output_json: str
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/repo_mesh/test_repo_loader.py -v`  
Expected: PASS

**Step 5: Commit**

```bash
git add repo_mesh/repo_loader.py repo_mesh/contracts.py tests/repo_mesh/test_repo_loader.py
git commit -m "feat: add selected repo loader and github auth preflight"
```

### Task 3: Implement Repo Owner Evidence Extraction

**Files:**
- Create: `repo_mesh/evidence.py`
- Create: `tests/repo_mesh/test_evidence.py`

**Step 1: Write the failing test**

```python
# tests/repo_mesh/test_evidence.py
from pathlib import Path


def test_extract_evidence_captures_intent_function_interest(tmp_path):
    from repo_mesh.evidence import extract_repo_evidence

    repo = tmp_path / "repo_a"
    repo.mkdir()
    (repo / "README.md").write_text(
        "# Habit tracker\nThis app helps users build daily focus habits.",
        encoding="utf-8",
    )
    (repo / "planner.py").write_text(
        "def plan_day(tasks):\n    return sorted(tasks)\n",
        encoding="utf-8",
    )

    items = extract_repo_evidence("repo-a", str(repo))
    types = {item.signal_type for item in items}
    assert "intention" in types
    assert "functionality" in types
    assert "interest" in types
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/repo_mesh/test_evidence.py -v`  
Expected: FAIL with import/module not found.

**Step 3: Write minimal implementation**

```python
# repo_mesh/evidence.py
from __future__ import annotations
from pathlib import Path
from repo_mesh.contracts import EvidenceItem


def _classify_text(text: str) -> list[tuple[str, str]]:
    lowered = text.lower()
    out: list[tuple[str, str]] = []
    if any(word in lowered for word in ["help", "improve", "support", "build"]):
        out.append(("intention", "User appears focused on helping or improving outcomes"))
    if any(word in lowered for word in ["def ", "class ", "function", "api", "pipeline"]):
        out.append(("functionality", "Repository emphasizes implementation mechanics"))
    if any(word in lowered for word in ["habit", "learning", "health", "productivity", "design"]):
        out.append(("interest", "Repository signals recurring personal/professional interests"))
    return out


def extract_repo_evidence(repo_id: str, repo_path: str) -> list[EvidenceItem]:
    root = Path(repo_path)
    if not root.exists():
        raise FileNotFoundError(repo_path)
    items: list[EvidenceItem] = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix not in {".md", ".py", ".ts", ".tsx", ".js", ".txt"}:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")[:5000]
        for idx, (signal_type, summary) in enumerate(_classify_text(text)):
            items.append(
                EvidenceItem(
                    evidence_id=f"{repo_id}:{path.name}:{idx}",
                    repo_id=repo_id,
                    signal_type=signal_type,
                    summary=summary,
                    source_ref=str(path),
                    weight=1.0,
                )
            )
    return items
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/repo_mesh/test_evidence.py -v`  
Expected: PASS

**Step 5: Commit**

```bash
git add repo_mesh/evidence.py tests/repo_mesh/test_evidence.py
git commit -m "feat: add repo evidence extraction for human-centered signals"
```

### Task 4: Implement Human-Centered Signal Inference per Repo Agent

**Files:**
- Create: `repo_mesh/profile.py`
- Create: `tests/repo_mesh/test_profile.py`

**Step 1: Write the failing test**

```python
# tests/repo_mesh/test_profile.py
from repo_mesh.contracts import EvidenceItem


def test_build_repo_profile_groups_skills_intentions_interests():
    from repo_mesh.profile import build_repo_profile

    evidence = [
        EvidenceItem("e1", "repo-a", "functionality", "API and pipeline design", "a.py", 1.0),
        EvidenceItem("e2", "repo-a", "intention", "Improve team collaboration", "README.md", 1.0),
        EvidenceItem("e3", "repo-a", "interest", "Learning systems and productivity", "README.md", 1.0),
    ]

    profile = build_repo_profile("repo-a", evidence)
    assert profile.repo_id == "repo-a"
    assert len(profile.skills) >= 1
    assert len(profile.intentions) >= 1
    assert len(profile.interests) >= 1
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/repo_mesh/test_profile.py -v`  
Expected: FAIL with import/module not found.

**Step 3: Write minimal implementation**

```python
# repo_mesh/profile.py
from __future__ import annotations
from repo_mesh.contracts import EvidenceItem, RepoProfile


def build_repo_profile(repo_id: str, evidence: list[EvidenceItem]) -> RepoProfile:
    skills: list[str] = []
    intentions: list[str] = []
    interests: list[str] = []
    evidence_ids: list[str] = []

    for item in evidence:
        evidence_ids.append(item.evidence_id)
        if item.signal_type == "functionality":
            skills.append(item.summary)
        elif item.signal_type == "intention":
            intentions.append(item.summary)
        elif item.signal_type == "interest":
            interests.append(item.summary)

    return RepoProfile(
        repo_id=repo_id,
        skills=sorted(set(skills)),
        intentions=sorted(set(intentions)),
        interests=sorted(set(interests)),
        evidence_ids=sorted(set(evidence_ids)),
    )
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/repo_mesh/test_profile.py -v`  
Expected: PASS

**Step 5: Commit**

```bash
git add repo_mesh/profile.py tests/repo_mesh/test_profile.py
git commit -m "feat: add repo-level profile inference"
```

### Task 5: Implement Cross-Repo Discussion and Consensus

**Files:**
- Create: `repo_mesh/discussion.py`
- Create: `tests/repo_mesh/test_discussion.py`

**Step 1: Write the failing test**

```python
# tests/repo_mesh/test_discussion.py
from repo_mesh.contracts import RepoProfile


def test_synthesize_profiles_builds_consensus_and_conflicts():
    from repo_mesh.discussion import synthesize_profiles

    profiles = [
        RepoProfile(
            repo_id="repo-a",
            skills=["pipeline design"],
            intentions=["improve collaboration"],
            interests=["productivity"],
            evidence_ids=["a1"],
        ),
        RepoProfile(
            repo_id="repo-b",
            skills=["pipeline design", "api integration"],
            intentions=["improve collaboration"],
            interests=["learning systems"],
            evidence_ids=["b1"],
        ),
    ]

    result = synthesize_profiles(profiles)
    assert "shared_skills" in result
    assert "shared_intentions" in result
    assert "interest_map" in result
    assert "pipeline design" in result["shared_skills"]
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/repo_mesh/test_discussion.py -v`  
Expected: FAIL with import/module not found.

**Step 3: Write minimal implementation**

```python
# repo_mesh/discussion.py
from __future__ import annotations
from collections import Counter
from repo_mesh.contracts import RepoProfile


def synthesize_profiles(profiles: list[RepoProfile]) -> dict:
    skill_counter: Counter[str] = Counter()
    intention_counter: Counter[str] = Counter()
    interest_map: dict[str, list[str]] = {}

    for profile in profiles:
        skill_counter.update(profile.skills)
        intention_counter.update(profile.intentions)
        for interest in profile.interests:
            interest_map.setdefault(interest, []).append(profile.repo_id)

    shared_skills = sorted([k for k, v in skill_counter.items() if v >= 2])
    shared_intentions = sorted([k for k, v in intention_counter.items() if v >= 2])

    return {
        "shared_skills": shared_skills,
        "shared_intentions": shared_intentions,
        "interest_map": {k: sorted(v) for k, v in interest_map.items()},
        "repo_count": len(profiles),
    }
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/repo_mesh/test_discussion.py -v`  
Expected: PASS

**Step 5: Commit**

```bash
git add repo_mesh/discussion.py tests/repo_mesh/test_discussion.py
git commit -m "feat: add cross-repo discussion synthesis"
```

### Task 6: Implement Coordinator Orchestration and On-Demand CLI

**Files:**
- Create: `repo_mesh/coordinator.py`
- Create: `repo_mesh/cli.py`
- Create: `tests/repo_mesh/test_cli_run.py`

**Step 1: Write the failing test**

```python
# tests/repo_mesh/test_cli_run.py
import json
import yaml


def test_run_once_writes_profile_output(tmp_path):
    from repo_mesh.coordinator import run_once

    repo_a = tmp_path / "repo_a"
    repo_a.mkdir()
    (repo_a / "README.md").write_text("Build tools to help teams learn faster", encoding="utf-8")

    repos_yaml = tmp_path / "repos.yaml"
    repos_yaml.write_text(
        yaml.safe_dump(
            {
                "repos": [
                    {
                        "repo_id": "repo-a",
                        "display_name": "Repo A",
                        "github_full_name": "org/repo-a",
                        "local_path": str(repo_a),
                        "selected": True,
                        "read_only": True,
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    out_json = tmp_path / "profile.json"
    run_once(str(repos_yaml), str(out_json))
    payload = json.loads(out_json.read_text(encoding="utf-8"))
    assert payload["repo_count"] == 1
    assert "profiles" in payload
    assert "consensus" in payload
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/repo_mesh/test_cli_run.py -v`  
Expected: FAIL with import/module not found.

**Step 3: Write minimal implementation**

```python
# repo_mesh/coordinator.py
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
```

```python
# repo_mesh/cli.py
from __future__ import annotations
import argparse
from repo_mesh.coordinator import run_once


def main() -> None:
    parser = argparse.ArgumentParser(description="Run human-centered repo agent mesh once")
    parser.add_argument("--repos", required=True, help="Path to repos.yaml")
    parser.add_argument("--out", required=True, help="Path to output JSON")
    args = parser.parse_args()
    run_once(args.repos, args.out)


if __name__ == "__main__":
    main()
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/repo_mesh/test_cli_run.py -v`  
Expected: PASS

**Step 5: Commit**

```bash
git add repo_mesh/coordinator.py repo_mesh/cli.py tests/repo_mesh/test_cli_run.py
git commit -m "feat: add on-demand coordinator and cli entrypoint"
```

### Task 7: Add Runbook, Prompt Contracts, and Full Verification

**Files:**
- Create: `repo_mesh/prompts/repo_owner_codex.prompt.md`
- Create: `repo_mesh/prompts/cross_repo_mediator_codex.prompt.md`
- Create: `repo_mesh/README.md`
- Create: `tests/repo_mesh/test_e2e_mesh.py`

**Step 1: Write the failing test**

```python
# tests/repo_mesh/test_e2e_mesh.py
from pathlib import Path


def test_prompt_contract_files_exist():
    assert Path("repo_mesh/prompts/repo_owner_codex.prompt.md").exists()
    assert Path("repo_mesh/prompts/cross_repo_mediator_codex.prompt.md").exists()
    assert Path("repo_mesh/README.md").exists()
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/repo_mesh/test_e2e_mesh.py -v`  
Expected: FAIL with missing file assertions.

**Step 3: Write minimal implementation**

```markdown
# repo_mesh/prompts/repo_owner_codex.prompt.md
You are the owner agent for one repository.
You are read-only.
Read repository code and text artifacts to infer:
1) likely user skills
2) likely user intentions
3) likely user interests
Return only JSON:
{
  "repo_id": "...",
  "skills": ["..."],
  "intentions": ["..."],
  "interests": ["..."],
  "evidence_refs": ["path#reason"]
}
```

```markdown
# repo_mesh/prompts/cross_repo_mediator_codex.prompt.md
You are the mediator agent.
Input: structured findings from multiple repository owner agents.
Task:
1) identify overlaps
2) identify disagreements
3) produce a human-centered unified summary
Do not request raw code unless absolutely required.
Return only JSON:
{
  "shared_skills": ["..."],
  "shared_intentions": ["..."],
  "interest_map": {"interest": ["repo-a", "repo-b"]},
  "conflicts": [{"topic": "...", "repos": ["..."], "reason": "..."}],
  "next_questions": ["..."]
}
```

```markdown
# repo_mesh/README.md
# repo_mesh

Read-only, on-demand, human-centered multi-repo agent mesh.

## Preconditions
- Selected repositories are already checked out locally.
- GitHub access configured with `GITHUB_TOKEN` or `gh auth login`.

## Run
python -m repo_mesh.cli --repos repo_mesh/config/repos.yaml --out repo_mesh/output/latest_profile.json
```

**Step 4: Run full verification**

Run: `pytest tests/repo_mesh -v`  
Expected: PASS

**Step 5: Commit**

```bash
git add repo_mesh tests/repo_mesh
git commit -m "docs: add codex prompt contracts and repo mesh runbook"
```

