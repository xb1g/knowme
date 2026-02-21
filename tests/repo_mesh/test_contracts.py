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
