from __future__ import annotations
import pandas as pd


def _score_row(i: int, total: int) -> tuple[float, float, float, float]:
    growth = max(40.0, 95.0 - i * (50.0 / max(1, total)))
    trend = max(35.0, 90.0 - i * (45.0 / max(1, total)))
    volume = max(30.0, 88.0 - i * (42.0 / max(1, total)))
    priority = round(0.5 * growth + 0.3 * trend + 0.2 * volume, 1)
    return round(growth, 1), round(trend, 1), round(volume, 1), priority


def run(in_csv: str, out_csv: str, shards: int = 8) -> None:
    df = pd.read_csv(in_csv).copy()
    df = df.reset_index(drop=True)
    out = []
    for i, row in df.iterrows():
        growth, trend, volume, priority = _score_row(i, len(df))
        out.append(
            {
                "category": row["category"],
                "growth_signal": growth,
                "posting_trend": trend,
                "posting_volume": volume,
                "priority_score": priority,
            }
        )
    pd.DataFrame(out).to_csv(out_csv, index=False)
