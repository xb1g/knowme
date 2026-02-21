from __future__ import annotations
import json
import pandas as pd


def run(in_csv: str, out_csv: str, schema_json: str) -> None:
    df = pd.read_csv(in_csv)
    schema = json.loads(open(schema_json, "r", encoding="utf-8").read())["columns"]

    checks = []
    checks.append(("schema_columns", "PASS" if list(df.columns) == schema else "FAIL", str(list(df.columns))))
    checks.append(("row_count_500", "PASS" if len(df) == 500 else "FAIL", str(len(df))))
    checks.append(("soft_ratio_min_0_30", "PASS" if (df["type"] == "soft").mean() >= 0.30 else "FAIL", str((df["type"] == "soft").mean())))
    checks.append(("score_range", "PASS" if ((df[["demand", "scarcity", "future_proof"]] >= 0).all().all() and (df[["demand", "scarcity", "future_proof"]] <= 100).all().all()) else "FAIL", "0-100"))
    checks.append(("no_duplicates", "PASS" if df["skill"].nunique() == len(df) else "FAIL", str(df["skill"].nunique())))

    pd.DataFrame(checks, columns=["check_name", "status", "details"]).to_csv(out_csv, index=False)
