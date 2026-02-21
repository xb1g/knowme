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


@dataclass(frozen=True)
class AgentRunContext:
    run_id: str
    repos_yaml: str
    policy_yaml: str
    output_json: str
