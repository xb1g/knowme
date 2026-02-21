from pathlib import Path
import pandas as pd


def test_stage_a1_writes_category_universe(tmp_path):
    from research_v2.pipeline.stage_a1_category_discovery import run

    out = tmp_path / "01_category_universe.csv"
    run(seed_yaml="research_v2/config/categories_seed.yaml", out_csv=str(out))

    df = pd.read_csv(out)
    assert list(df.columns) == ["category", "aliases", "priority_seed"]
    assert len(df) >= 25
    assert "Design" in set(df["category"])
