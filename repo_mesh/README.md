# repo_mesh

Read-only, on-demand, human-centered multi-repo agent mesh.

## Preconditions
- Selected repositories are already checked out locally.
- GitHub access configured with `GITHUB_TOKEN` or `gh auth login`.

## Run
```
python -m repo_mesh.cli --repos repo_mesh/config/repos.yaml --out repo_mesh/output/latest_profile.json
```
