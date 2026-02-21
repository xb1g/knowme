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
