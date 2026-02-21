import pandas as pd


def test_stage_b2_generates_large_evidence_table(tmp_path):
    from research_v2.pipeline.stage_b2_skill_mining import run

    in_csv = tmp_path / "03_category_subdomains.csv"
    pd.DataFrame(
        [{"category": "Design", "subdomain": f"Design S{i}", "role_family": "Practitioner"} for i in range(12)]
    ).to_csv(in_csv, index=False)

    out_csv = tmp_path / "04_raw_skill_evidence.csv"
    run(str(in_csv), str(out_csv), min_rows=120)
    df = pd.read_csv(out_csv)

    required = {
        "skill_raw", "category", "subdomain", "type_hint",
        "growth", "posting_trend", "posting_volume",
        "openings_ratio", "skills_gap",
        "durability", "automation_resilience", "cross_sector_use"
    }
    assert set(df.columns) == required
    assert len(df) >= 120
