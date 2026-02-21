import pandas as pd


def test_stage_c4_writes_quality_report(tmp_path):
    from research_v2.pipeline.stage_c4_quality_gate import run

    in_csv = tmp_path / "08_skill_top200.csv"
    rows = []
    for i in range(200):
        rows.append(
            {"skill": f"Skill{i}", "category": "Soft Skills" if i < 70 else "Technology", "type": "soft" if i < 70 else "hard",
             "demand": 90 - i*0.1, "scarcity": 70, "future_proof": 80}
        )
    pd.DataFrame(rows).to_csv(in_csv, index=False)

    out_csv = tmp_path / "09_quality_report.csv"
    run(str(in_csv), str(out_csv), "research_v2/config/final_schema.json")

    report = pd.read_csv(out_csv)
    assert "schema_columns" in set(report["check_name"])
    assert set(report["status"]) <= {"PASS", "FAIL"}
