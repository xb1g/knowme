from __future__ import annotations
import pandas as pd


def run(in_csv: str, out_csv: str, top_n: int = 200, min_soft_ratio: float = 0.30) -> None:
    df = pd.read_csv(in_csv).copy()
    df["type"] = df["type_hint"].map(lambda x: "soft" if str(x).lower() == "soft" else "hard")

    ranked = df.sort_values(["demand", "scarcity"], ascending=[False, False])
    top = ranked.head(top_n).copy()

    needed_soft = int(top_n * min_soft_ratio)
    current_soft = int((top["type"] == "soft").sum())

    if current_soft < needed_soft:
        shortfall = needed_soft - current_soft
        extra_soft = ranked.iloc[top_n:][ranked.iloc[top_n:]["type"] == "soft"].head(shortfall)
        hard_to_drop = top[top["type"] == "hard"].sort_values(["demand", "scarcity"]).head(shortfall)
        top = top.drop(index=hard_to_drop.index)
        top = pd.concat([top, extra_soft], ignore_index=True)
        top = top.sort_values(["demand", "scarcity"], ascending=[False, False]).head(top_n)

    out = top[["skill", "category", "type", "demand", "scarcity", "future_proof"]]
    out.to_csv(out_csv, index=False)
