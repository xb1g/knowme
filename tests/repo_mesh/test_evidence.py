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
