import pandas as pd


def test_stage_c3_outputs_top_200_and_soft_quota(tmp_path):
    from research_v2.pipeline.stage_c3_rank import run

    rows = []
    for i in range(260):
        rows.append(
            {
                "skill": f"Skill{i}",
                "category": "Technology" if i % 3 else "Soft Skills",
                "type_hint": "soft" if i % 3 == 0 else "hard",
                "demand": 100 - (i * 0.2),
                "scarcity": 70,
                "future_proof": 75,
            }
        )
    in_csv = tmp_path / "07_skill_scored.csv"
    pd.DataFrame(rows).to_csv(in_csv, index=False)

    out_csv = tmp_path / "08_skill_top200.csv"
    run(str(in_csv), str(out_csv), top_n=200, min_soft_ratio=0.30)

    df = pd.read_csv(out_csv)
    assert len(df) == 200
    assert (df["type"] == "soft").mean() >= 0.30
    assert list(df.columns) == ["skill", "category", "type", "demand", "scarcity", "future_proof"]
