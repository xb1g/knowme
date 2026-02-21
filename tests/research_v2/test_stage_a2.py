import pandas as pd


def test_stage_a2_outputs_required_signals(tmp_path):
    from research_v2.pipeline.stage_a2_category_triage import run

    in_csv = tmp_path / "01_category_universe.csv"
    pd.DataFrame(
        [{"category": f"Cat{i}", "aliases": "x", "priority_seed": 50} for i in range(30)]
    ).to_csv(in_csv, index=False)

    out_csv = tmp_path / "02_category_signals.csv"
    run(str(in_csv), str(out_csv), shards=6)
    df = pd.read_csv(out_csv)

    assert set(df.columns) == {
        "category", "growth_signal", "posting_trend", "posting_volume", "priority_score"
    }
    assert len(df) == 30
