from __future__ import annotations
from pathlib import Path
import shutil

from research_v2.pipeline.stage_a1_category_discovery import run as a1
from research_v2.pipeline.stage_a2_category_triage import run as a2
from research_v2.pipeline.stage_b1_subdomains import run as b1
from research_v2.pipeline.stage_b2_skill_mining import run as b2
from research_v2.pipeline.stage_c1_normalize import run as c1
from research_v2.pipeline.stage_c2_score import run as c2
from research_v2.pipeline.stage_c3_rank import run as c3
from research_v2.pipeline.stage_c4_quality_gate import run as c4

CONFIG_DIR = Path(__file__).parent.parent / "config"


def run_all(base_dir: str = "research_v2", out_dir: str = "research_v2/output") -> None:
    base = Path(base_dir)
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    # Use package config dir if base_dir doesn't have config (e.g. in tmp_path tests)
    cfg = base / "config"
    if not cfg.exists():
        cfg = CONFIG_DIR

    p1 = out / "01_category_universe.csv"
    p2 = out / "02_category_signals.csv"
    p3 = out / "03_category_subdomains.csv"
    p4 = out / "04_raw_skill_evidence.csv"
    p5 = out / "05_skill_canonical_map.csv"
    p6 = out / "06_normalized_skill_evidence.csv"
    p7 = out / "07_skill_scored.csv"
    p8 = out / "08_skill_top200.csv"
    p9 = out / "09_quality_report.csv"
    final = out / "skills_demand_ranking_v2.csv"

    a1(str(cfg / "categories_seed.yaml"), str(p1))
    a2(str(p1), str(p2), shards=8)
    b1(str(p2), str(p3), keep_top=18)
    b2(str(p3), str(p4), min_rows=1200)
    c1(str(p4), str(p5), str(p6), str(cfg / "synonyms.yaml"))
    c2(str(p6), str(p7), str(cfg / "scoring_weights.yaml"))
    c3(str(p7), str(p8), top_n=200, min_soft_ratio=0.30)
    c4(str(p8), str(p9), str(cfg / "final_schema.json"))

    shutil.copyfile(p8, final)


if __name__ == "__main__":
    run_all()
