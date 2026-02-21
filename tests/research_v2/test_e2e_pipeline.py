from pathlib import Path
import pandas as pd


def test_e2e_pipeline_generates_final_csv(tmp_path):
    from research_v2.pipeline.run_pipeline import run_all

    out_dir = tmp_path / "output"
    run_all(base_dir=str(tmp_path), out_dir=str(out_dir))

    final_csv = out_dir / "skills_demand_ranking_v2.csv"
    assert final_csv.exists()
    df = pd.read_csv(final_csv)
    assert list(df.columns) == ["skill", "category", "type", "demand", "scarcity", "future_proof"]
    assert len(df) == 200
