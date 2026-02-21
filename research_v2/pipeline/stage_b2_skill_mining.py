from __future__ import annotations
import random
import pandas as pd

SKILLS = [
    ("Python", "hard"), ("SQL", "hard"), ("Data visualization", "hard"),
    ("Communication", "soft"), ("Problem solving", "soft"), ("Leadership", "soft"),
    ("Project management", "hard"), ("Figma", "hard"), ("AutoCAD", "hard"),
    ("Negotiation", "soft"), ("Customer empathy", "soft"), ("Quality assurance", "hard"),
]


def run(in_csv: str, out_csv: str, min_rows: int = 1200) -> None:
    random.seed(7)
    domains = pd.read_csv(in_csv)
    rows = []
    while len(rows) < min_rows:
        for _, d in domains.iterrows():
            for skill_raw, type_hint in SKILLS:
                rows.append(
                    {
                        "skill_raw": skill_raw,
                        "category": d["category"],
                        "subdomain": d["subdomain"],
                        "type_hint": type_hint,
                        "growth": random.uniform(45, 98),
                        "posting_trend": random.uniform(40, 96),
                        "posting_volume": random.uniform(35, 95),
                        "openings_ratio": random.uniform(45, 96),
                        "skills_gap": random.uniform(40, 92),
                        "durability": random.uniform(50, 99),
                        "automation_resilience": random.uniform(45, 97),
                        "cross_sector_use": random.uniform(50, 99),
                    }
                )
            if len(rows) >= min_rows:
                break
    pd.DataFrame(rows).to_csv(out_csv, index=False)
