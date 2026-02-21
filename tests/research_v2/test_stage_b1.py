import pandas as pd


def test_stage_b1_selects_top_categories_and_expands(tmp_path):
    from research_v2.pipeline.stage_b1_subdomains import run

    in_csv = tmp_path / "02_category_signals.csv"
    pd.DataFrame(
        [{"category": f"Cat{i}", "growth_signal": 90-i, "posting_trend": 85-i, "posting_volume": 80-i, "priority_score": 95-i} for i in range(25)]
    ).to_csv(in_csv, index=False)

    out_csv = tmp_path / "03_category_subdomains.csv"
    run(str(in_csv), str(out_csv), keep_top=18)
    df = pd.read_csv(out_csv)

    assert set(df.columns) == {"category", "subdomain", "role_family"}
    assert df["category"].nunique() == 18
