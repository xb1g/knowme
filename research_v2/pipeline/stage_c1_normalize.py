from __future__ import annotations
import pandas as pd
import yaml


def run(in_csv: str, map_csv: str, out_csv: str, synonyms_yaml: str) -> None:
    df = pd.read_csv(in_csv).copy()
    synonyms = yaml.safe_load(open(synonyms_yaml, "r", encoding="utf-8"))

    df["skill"] = df["skill_raw"].map(lambda s: synonyms.get(s, s))

    mapping = df[["skill_raw", "skill"]].drop_duplicates().rename(columns={"skill": "skill_canonical"})
    mapping["merge_confidence"] = 1.0

    norm = df.drop(columns=["skill_raw"]).copy()
    norm.to_csv(out_csv, index=False)
    mapping.to_csv(map_csv, index=False)
