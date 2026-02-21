from __future__ import annotations
import csv
import yaml

DEFAULT_EXPANSION = [
    "Architecture", "Construction", "Manufacturing", "Energy", "Transportation",
    "Retail", "E-commerce", "Banking", "Insurance", "Public Sector",
    "Education", "Legal", "Media", "Hospitality", "Agriculture",
    "Biotech", "Pharma", "Telecom", "Cybersecurity", "Product Management",
    "Human Resources", "Supply Chain", "Marketing", "Customer Support"
]


def run(seed_yaml: str, out_csv: str) -> None:
    with open(seed_yaml, "r", encoding="utf-8") as f:
        seed = yaml.safe_load(f)["categories"]
    categories = list(dict.fromkeys(seed + DEFAULT_EXPANSION))

    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["category", "aliases", "priority_seed"])
        for idx, cat in enumerate(categories):
            writer.writerow([cat, cat.lower(), max(1, 100 - idx)])
