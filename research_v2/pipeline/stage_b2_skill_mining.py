from __future__ import annotations
import random
import pandas as pd

SKILLS = [
    # Technology / Engineering
    ("Python", "hard"), ("SQL", "hard"), ("JavaScript", "hard"), ("TypeScript", "hard"),
    ("React", "hard"), ("Node.js", "hard"), ("Docker", "hard"), ("Kubernetes", "hard"),
    ("AWS", "hard"), ("Git", "hard"), ("REST API design", "hard"), ("GraphQL", "hard"),
    ("CI/CD", "hard"), ("Linux", "hard"), ("Terraform", "hard"),
    # Data / Analytics
    ("Data visualization", "hard"), ("Machine learning", "hard"), ("Deep learning", "hard"),
    ("pandas", "hard"), ("Spark", "hard"), ("Tableau", "hard"), ("Power BI", "hard"),
    ("A/B testing", "hard"), ("Statistical analysis", "hard"),
    # Design / Creative
    ("Figma", "hard"), ("AutoCAD", "hard"), ("Adobe Illustrator", "hard"),
    ("UX research", "hard"), ("Wireframing", "hard"), ("Motion design", "hard"),
    # Healthcare
    ("Electronic health records", "hard"), ("Clinical documentation", "hard"),
    ("Medical coding", "hard"), ("Patient triage", "hard"), ("HIPAA compliance", "hard"),
    # Business / Management
    ("Project management", "hard"), ("Agile / Scrum", "hard"), ("Quality assurance", "hard"),
    ("Financial modeling", "hard"), ("Supply chain management", "hard"),
    # Soft skills
    ("Communication", "soft"), ("Problem solving", "soft"), ("Leadership", "soft"),
    ("Negotiation", "soft"), ("Customer empathy", "soft"), ("Critical thinking", "soft"),
    ("Adaptability", "soft"), ("Collaboration", "soft"), ("Time management", "soft"),
    ("Emotional intelligence", "soft"), ("Conflict resolution", "soft"),
    ("Creativity", "soft"), ("Decision making", "soft"),
]


def run(in_csv: str, out_csv: str, min_rows: int = 3000) -> None:
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
