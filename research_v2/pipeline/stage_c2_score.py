from __future__ import annotations
import pandas as pd
import yaml


def run(in_csv: str, out_csv: str, weights_yaml: str) -> None:
    w = yaml.safe_load(open(weights_yaml, "r", encoding="utf-8"))
    df = pd.read_csv(in_csv).copy()

    df["demand"] = (
        w["demand"]["growth"] * df["growth"]
        + w["demand"]["posting_trend"] * df["posting_trend"]
        + w["demand"]["posting_volume"] * df["posting_volume"]
    ).round(1)

    df["scarcity"] = (
        w["scarcity"]["openings_ratio"] * df["openings_ratio"]
        + w["scarcity"]["skills_gap"] * df["skills_gap"]
    ).round(1)

    df["future_proof"] = (
        w["future_proof"]["durability"] * df["durability"]
        + w["future_proof"]["automation_resilience"] * df["automation_resilience"]
        + w["future_proof"]["cross_sector_use"] * df["cross_sector_use"]
    ).round(1)

    df.to_csv(out_csv, index=False)
