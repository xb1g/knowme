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
