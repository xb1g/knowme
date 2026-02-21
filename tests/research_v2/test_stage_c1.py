import pandas as pd


def test_stage_c1_merges_synonyms(tmp_path):
    from research_v2.pipeline.stage_c1_normalize import run

    raw = tmp_path / "04_raw_skill_evidence.csv"
    pd.DataFrame([
        {"skill_raw": "JS", "category": "Technology", "subdomain": "Web", "type_hint": "hard",
         "growth": 80, "posting_trend": 82, "posting_volume": 81,
         "openings_ratio": 79, "skills_gap": 70, "durability": 78,
         "automation_resilience": 75, "cross_sector_use": 84},
        {"skill_raw": "JavaScript", "category": "Technology", "subdomain": "Web", "type_hint": "hard",
         "growth": 82, "posting_trend": 81, "posting_volume": 80,
         "openings_ratio": 78, "skills_gap": 71, "durability": 79,
         "automation_resilience": 74, "cross_sector_use": 85},
    ]).to_csv(raw, index=False)

    map_csv = tmp_path / "05_skill_canonical_map.csv"
    out_csv = tmp_path / "06_normalized_skill_evidence.csv"
    run(str(raw), str(map_csv), str(out_csv), "research_v2/config/synonyms.yaml")

    m = pd.read_csv(map_csv)
    n = pd.read_csv(out_csv)
    assert "JavaScript" in set(m["skill_canonical"])
    assert set(n["skill"]) == {"JavaScript"}
