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
