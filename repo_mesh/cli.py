from __future__ import annotations
import argparse
from repo_mesh.coordinator import run_once


def main() -> None:
    parser = argparse.ArgumentParser(description="Run human-centered repo agent mesh once")
    parser.add_argument("--repos", required=True, help="Path to repos.yaml")
    parser.add_argument("--out", required=True, help="Path to output JSON")
    args = parser.parse_args()
    run_once(args.repos, args.out)


if __name__ == "__main__":
    main()
