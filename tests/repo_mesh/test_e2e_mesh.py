from pathlib import Path


def test_prompt_contract_files_exist():
    assert Path("repo_mesh/prompts/repo_owner_codex.prompt.md").exists()
    assert Path("repo_mesh/prompts/cross_repo_mediator_codex.prompt.md").exists()
    assert Path("repo_mesh/README.md").exists()
