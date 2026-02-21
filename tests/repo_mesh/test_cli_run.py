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
