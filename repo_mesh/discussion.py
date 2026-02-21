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
