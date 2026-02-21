import pandas as pd


def test_stage_c2_applies_weighted_formulas(tmp_path):
    from research_v2.pipeline.stage_c2_score import run

    in_csv = tmp_path / "06_normalized_skill_evidence.csv"
    pd.DataFrame([
        {"skill": "Python", "category": "Technology", "subdomain": "Core", "type_hint": "hard",
         "growth": 90, "posting_trend": 80, "posting_volume": 70,
         "openings_ratio": 85, "skills_gap": 60,
         "durability": 88, "automation_resilience": 72, "cross_sector_use": 84}
    ]).to_csv(in_csv, index=False)

    out_csv = tmp_path / "07_skill_scored.csv"
    run(str(in_csv), str(out_csv), "research_v2/config/scoring_weights.yaml")
    df = pd.read_csv(out_csv)

    assert round(float(df.loc[0, "demand"]), 1) == 84.0
    assert round(float(df.loc[0, "scarcity"]), 1) == 77.5
    assert round(float(df.loc[0, "future_proof"]), 1) == 81.6
