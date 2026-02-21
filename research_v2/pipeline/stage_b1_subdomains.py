from __future__ import annotations
import pandas as pd

SUBDOMAIN_TEMPLATE = [
    ("Core", "Practitioner"),
    ("Strategy", "Lead"),
    ("Operations", "Specialist"),
]


def run(in_csv: str, out_csv: str, keep_top: int = 18) -> None:
    triage = pd.read_csv(in_csv).sort_values("priority_score", ascending=False).head(keep_top)
    rows = []
    for _, row in triage.iterrows():
        for subdomain, role_family in SUBDOMAIN_TEMPLATE:
            rows.append(
                {
                    "category": row["category"],
                    "subdomain": f"{row['category']} {subdomain}",
                    "role_family": role_family,
                }
            )
    pd.DataFrame(rows).to_csv(out_csv, index=False)
