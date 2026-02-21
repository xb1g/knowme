from __future__ import annotations
import re
from repo_mesh.contracts import EvidenceItem, RepoProfile


def _extract_skill_name(summary: str) -> str:
    """Extract [Skill Name] from summary, or return summary as-is."""
    m = re.match(r"\[(.+?)\]", summary)
    return m.group(1) if m else summary


def build_repo_profile(repo_id: str, evidence: list[EvidenceItem]) -> RepoProfile:
    skills: list[str] = []
    intentions: list[str] = []
    interests: list[str] = []
    evidence_ids: list[str] = []

    for item in evidence:
        evidence_ids.append(item.evidence_id)
        name = _extract_skill_name(item.summary)
        if item.signal_type == "functionality":
            skills.append(name)
        elif item.signal_type == "intention":
            intentions.append(name)
        elif item.signal_type == "interest":
            interests.append(name)

    return RepoProfile(
        repo_id=repo_id,
        skills=sorted(set(skills)),
        intentions=sorted(set(intentions)),
        interests=sorted(set(interests)),
        evidence_ids=sorted(set(evidence_ids)),
    )
