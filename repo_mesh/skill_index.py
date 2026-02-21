from __future__ import annotations
import csv
from pathlib import Path
from dataclasses import dataclass


@dataclass(frozen=True)
class Skill:
    name: str
    category: str
    type: str   # "hard" or "soft"
    demand: float
    scarcity: float
    future_proof: float


def load_skill_index(by_category_dir: str | None = None) -> list[Skill]:
    """Load all skills from by_category CSV files."""
    if by_category_dir is None:
        # resolve relative to this file: repo_mesh/../research_v2/output/by_category
        by_category_dir = str(Path(__file__).parent.parent / "research_v2" / "output" / "by_category")

    skills: list[Skill] = []
    seen: set[str] = set()
    for csv_path in sorted(Path(by_category_dir).glob("*.csv")):
        for row in csv.DictReader(csv_path.open(encoding="utf-8")):
            name = row["skill"].strip()
            if name.lower() in seen:
                continue
            seen.add(name.lower())
            skills.append(Skill(
                name=name,
                category=row["category"].strip(),
                type=row["type"].strip(),
                demand=float(row["demand"]),
                scarcity=float(row["scarcity"]),
                future_proof=float(row["future_proof"]),
            ))
    return skills
