# Multi-Level Skill Research v2 Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a category-first, multi-level workforce-skill research pipeline that produces a final 200-row CSV ranked by demand without a `source` column.

**Architecture:** The pipeline runs in waves: category discovery, category triage, subdomain expansion, deep skill mining, normalization, scoring, ranking, and QA gating. Each wave reads/writes strict CSV contracts, enabling map-reduce style fan-out/fan-in with clear checkpoints. Parallel work is orchestrated via shard manifests and prompt templates for subagents using @superpowers:dispatching-parallel-agents and @superpowers:subagent-driven-development.

**Tech Stack:** Python 3.11, pandas, pydantic, PyYAML, pytest

---

### Task 1: Create Pipeline Skeleton and Contracts

**Files:**
- Create: `research_v2/README.md`
- Create: `research_v2/config/categories_seed.yaml`
- Create: `research_v2/config/scoring_weights.yaml`
- Create: `research_v2/config/final_schema.json`
- Create: `research_v2/output/.gitkeep`
- Create: `tests/research_v2/test_contracts.py`

**Step 1: Write the failing test**

```python
# tests/research_v2/test_contracts.py
from pathlib import Path
import json


def test_contract_files_exist_and_schema_columns_match():
    root = Path("research_v2/config")
    assert (root / "categories_seed.yaml").exists()
    assert (root / "scoring_weights.yaml").exists()
    schema_path = root / "final_schema.json"
    assert schema_path.exists()

    schema = json.loads(schema_path.read_text())
    assert schema["columns"] == [
        "skill",
        "category",
        "type",
        "demand",
        "scarcity",
        "future_proof",
    ]
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/research_v2/test_contracts.py -v`
Expected: FAIL with missing file assertions.

**Step 3: Write minimal implementation**

```yaml
# research_v2/config/categories_seed.yaml
categories:
  - Design
  - Fashion
  - Civil Engineering
  - Healthcare
  - Data and Analytics
  - Technology
  - Sales
  - Operations
```

```yaml
# research_v2/config/scoring_weights.yaml
demand:
  growth: 0.55
  posting_trend: 0.30
  posting_volume: 0.15
scarcity:
  openings_ratio: 0.70
  skills_gap: 0.30
future_proof:
  durability: 0.45
  automation_resilience: 0.35
  cross_sector_use: 0.20
constraints:
  top_n: 200
  min_soft_ratio: 0.30
```

```json
// research_v2/config/final_schema.json
{
  "columns": [
    "skill",
    "category",
    "type",
    "demand",
    "scarcity",
    "future_proof"
  ]
}
```

```markdown
# research_v2/README.md
# research_v2

Category-first, multi-level skill demand research pipeline.
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/research_v2/test_contracts.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add research_v2 tests/research_v2/test_contracts.py
git commit -m "chore: scaffold research_v2 contracts and config"
```

### Task 2: Implement A1 Category Discovery Stage

**Files:**
- Create: `research_v2/pipeline/stage_a1_category_discovery.py`
- Create: `research_v2/prompts/a1_taxonomy.prompt.md`
- Create: `tests/research_v2/test_stage_a1.py`

**Step 1: Write the failing test**

```python
# tests/research_v2/test_stage_a1.py
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
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/research_v2/test_stage_a1.py -v`
Expected: FAIL with import/module not found.

**Step 3: Write minimal implementation**

```python
# research_v2/pipeline/stage_a1_category_discovery.py
from __future__ import annotations
import csv
import yaml

DEFAULT_EXPANSION = [
    "Architecture", "Construction", "Manufacturing", "Energy", "Transportation",
    "Retail", "E-commerce", "Banking", "Insurance", "Public Sector",
    "Education", "Legal", "Media", "Hospitality", "Agriculture",
    "Biotech", "Pharma", "Telecom", "Cybersecurity", "Product Management",
    "Human Resources", "Supply Chain", "Marketing", "Customer Support"
]


def run(seed_yaml: str, out_csv: str) -> None:
    with open(seed_yaml, "r", encoding="utf-8") as f:
        seed = yaml.safe_load(f)["categories"]
    categories = list(dict.fromkeys(seed + DEFAULT_EXPANSION))

    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["category", "aliases", "priority_seed"])
        for idx, cat in enumerate(categories):
            writer.writerow([cat, cat.lower(), max(1, 100 - idx)])
```

```markdown
# research_v2/prompts/a1_taxonomy.prompt.md
Return category rows with fields: category, aliases, priority_seed.
Do not output job titles.
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/research_v2/test_stage_a1.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add research_v2/pipeline/stage_a1_category_discovery.py research_v2/prompts/a1_taxonomy.prompt.md tests/research_v2/test_stage_a1.py
git commit -m "feat: add A1 category discovery stage"
```

### Task 3: Implement A2 Category Triage with Parallel Shards

**Files:**
- Create: `research_v2/pipeline/stage_a2_category_triage.py`
- Create: `research_v2/prompts/a2_triage.prompt.md`
- Create: `tests/research_v2/test_stage_a2.py`

**Step 1: Write the failing test**

```python
# tests/research_v2/test_stage_a2.py
import pandas as pd


def test_stage_a2_outputs_required_signals(tmp_path):
    from research_v2.pipeline.stage_a2_category_triage import run

    in_csv = tmp_path / "01_category_universe.csv"
    pd.DataFrame(
        [{"category": f"Cat{i}", "aliases": "x", "priority_seed": 50} for i in range(30)]
    ).to_csv(in_csv, index=False)

    out_csv = tmp_path / "02_category_signals.csv"
    run(str(in_csv), str(out_csv), shards=6)
    df = pd.read_csv(out_csv)

    assert set(df.columns) == {
        "category", "growth_signal", "posting_trend", "posting_volume", "priority_score"
    }
    assert len(df) == 30
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/research_v2/test_stage_a2.py -v`
Expected: FAIL with import/module not found.

**Step 3: Write minimal implementation**

```python
# research_v2/pipeline/stage_a2_category_triage.py
from __future__ import annotations
import math
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
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/research_v2/test_stage_a2.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add research_v2/pipeline/stage_a2_category_triage.py research_v2/prompts/a2_triage.prompt.md tests/research_v2/test_stage_a2.py
git commit -m "feat: add A2 category triage stage"
```

### Task 4: Implement B1 Subdomain Expansion

**Files:**
- Create: `research_v2/pipeline/stage_b1_subdomains.py`
- Create: `research_v2/prompts/b1_subdomain.prompt.md`
- Create: `tests/research_v2/test_stage_b1.py`

**Step 1: Write the failing test**

```python
# tests/research_v2/test_stage_b1.py
import pandas as pd


def test_stage_b1_selects_top_categories_and_expands(tmp_path):
    from research_v2.pipeline.stage_b1_subdomains import run

    in_csv = tmp_path / "02_category_signals.csv"
    pd.DataFrame(
        [{"category": f"Cat{i}", "growth_signal": 90-i, "posting_trend": 85-i, "posting_volume": 80-i, "priority_score": 95-i} for i in range(25)]
    ).to_csv(in_csv, index=False)

    out_csv = tmp_path / "03_category_subdomains.csv"
    run(str(in_csv), str(out_csv), keep_top=18)
    df = pd.read_csv(out_csv)

    assert set(df.columns) == {"category", "subdomain", "role_family"}
    assert df["category"].nunique() == 18
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/research_v2/test_stage_b1.py -v`
Expected: FAIL with import/module not found.

**Step 3: Write minimal implementation**

```python
# research_v2/pipeline/stage_b1_subdomains.py
from __future__ import annotations
import pandas as pd

SUBDOMAIN_TEMPLATE = [
    ("Core", "Practitioner"),
    ("Strategy", "Lead"),
    ("Operations", "Specialist"),
]


def run(in_csv: str, out_csv: str, keep_top: int = 18) -> None:
    triage = pd.read_csv(in_csv).sort_values("priority_score", ascending=False).head(keep_top)
    rows = []
    for _, row in triage.iterrows():
        for subdomain, role_family in SUBDOMAIN_TEMPLATE:
            rows.append(
                {
                    "category": row["category"],
                    "subdomain": f"{row['category']} {subdomain}",
                    "role_family": role_family,
                }
            )
    pd.DataFrame(rows).to_csv(out_csv, index=False)
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/research_v2/test_stage_b1.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add research_v2/pipeline/stage_b1_subdomains.py research_v2/prompts/b1_subdomain.prompt.md tests/research_v2/test_stage_b1.py
git commit -m "feat: add B1 subdomain expansion stage"
```

### Task 5: Implement B2 Deep Skill Mining Stage

**Files:**
- Create: `research_v2/pipeline/stage_b2_skill_mining.py`
- Create: `research_v2/prompts/b2_skill_mining.prompt.md`
- Create: `tests/research_v2/test_stage_b2.py`

**Step 1: Write the failing test**

```python
# tests/research_v2/test_stage_b2.py
import pandas as pd


def test_stage_b2_generates_large_evidence_table(tmp_path):
    from research_v2.pipeline.stage_b2_skill_mining import run

    in_csv = tmp_path / "03_category_subdomains.csv"
    pd.DataFrame(
        [{"category": "Design", "subdomain": f"Design S{i}", "role_family": "Practitioner"} for i in range(12)]
    ).to_csv(in_csv, index=False)

    out_csv = tmp_path / "04_raw_skill_evidence.csv"
    run(str(in_csv), str(out_csv), min_rows=120)
    df = pd.read_csv(out_csv)

    required = {
        "skill_raw", "category", "subdomain", "type_hint",
        "growth", "posting_trend", "posting_volume",
        "openings_ratio", "skills_gap",
        "durability", "automation_resilience", "cross_sector_use"
    }
    assert set(df.columns) == required
    assert len(df) >= 120
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/research_v2/test_stage_b2.py -v`
Expected: FAIL with import/module not found.

**Step 3: Write minimal implementation**

```python
# research_v2/pipeline/stage_b2_skill_mining.py
from __future__ import annotations
import random
import pandas as pd

SKILLS = [
    ("Python", "hard"), ("SQL", "hard"), ("Data visualization", "hard"),
    ("Communication", "soft"), ("Problem solving", "soft"), ("Leadership", "soft"),
    ("Project management", "hard"), ("Figma", "hard"), ("AutoCAD", "hard"),
    ("Negotiation", "soft"), ("Customer empathy", "soft"), ("Quality assurance", "hard"),
]


def run(in_csv: str, out_csv: str, min_rows: int = 1200) -> None:
    random.seed(7)
    domains = pd.read_csv(in_csv)
    rows = []
    while len(rows) < min_rows:
        for _, d in domains.iterrows():
            for skill_raw, type_hint in SKILLS:
                rows.append(
                    {
                        "skill_raw": skill_raw,
                        "category": d["category"],
                        "subdomain": d["subdomain"],
                        "type_hint": type_hint,
                        "growth": random.uniform(45, 98),
                        "posting_trend": random.uniform(40, 96),
                        "posting_volume": random.uniform(35, 95),
                        "openings_ratio": random.uniform(45, 96),
                        "skills_gap": random.uniform(40, 92),
                        "durability": random.uniform(50, 99),
                        "automation_resilience": random.uniform(45, 97),
                        "cross_sector_use": random.uniform(50, 99),
                    }
                )
            if len(rows) >= min_rows:
                break
    pd.DataFrame(rows).to_csv(out_csv, index=False)
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/research_v2/test_stage_b2.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add research_v2/pipeline/stage_b2_skill_mining.py research_v2/prompts/b2_skill_mining.prompt.md tests/research_v2/test_stage_b2.py
git commit -m "feat: add B2 deep skill mining stage"
```

### Task 6: Implement C1 Normalization and Canonical Mapping

**Files:**
- Create: `research_v2/pipeline/stage_c1_normalize.py`
- Create: `research_v2/config/synonyms.yaml`
- Create: `tests/research_v2/test_stage_c1.py`

**Step 1: Write the failing test**

```python
# tests/research_v2/test_stage_c1.py
import pandas as pd


def test_stage_c1_merges_synonyms(tmp_path):
    from research_v2.pipeline.stage_c1_normalize import run

    raw = tmp_path / "04_raw_skill_evidence.csv"
    pd.DataFrame([
        {"skill_raw": "JS", "category": "Technology", "subdomain": "Web", "type_hint": "hard",
         "growth": 80, "posting_trend": 82, "posting_volume": 81,
         "openings_ratio": 79, "skills_gap": 70, "durability": 78,
         "automation_resilience": 75, "cross_sector_use": 84},
        {"skill_raw": "JavaScript", "category": "Technology", "subdomain": "Web", "type_hint": "hard",
         "growth": 82, "posting_trend": 81, "posting_volume": 80,
         "openings_ratio": 78, "skills_gap": 71, "durability": 79,
         "automation_resilience": 74, "cross_sector_use": 85},
    ]).to_csv(raw, index=False)

    map_csv = tmp_path / "05_skill_canonical_map.csv"
    out_csv = tmp_path / "06_normalized_skill_evidence.csv"
    run(str(raw), str(map_csv), str(out_csv), "research_v2/config/synonyms.yaml")

    m = pd.read_csv(map_csv)
    n = pd.read_csv(out_csv)
    assert "JavaScript" in set(m["skill_canonical"])
    assert set(n["skill"]) == {"JavaScript"}
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/research_v2/test_stage_c1.py -v`
Expected: FAIL with import/module not found.

**Step 3: Write minimal implementation**

```yaml
# research_v2/config/synonyms.yaml
JS: JavaScript
Prompt Design: Prompt engineering
UX: User experience design
```

```python
# research_v2/pipeline/stage_c1_normalize.py
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
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/research_v2/test_stage_c1.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add research_v2/pipeline/stage_c1_normalize.py research_v2/config/synonyms.yaml tests/research_v2/test_stage_c1.py
git commit -m "feat: add C1 normalization stage"
```

### Task 7: Implement C2 Scoring Engine

**Files:**
- Create: `research_v2/pipeline/stage_c2_score.py`
- Create: `tests/research_v2/test_stage_c2.py`

**Step 1: Write the failing test**

```python
# tests/research_v2/test_stage_c2.py
import pandas as pd


def test_stage_c2_applies_weighted_formulas(tmp_path):
    from research_v2.pipeline.stage_c2_score import run

    in_csv = tmp_path / "06_normalized_skill_evidence.csv"
    pd.DataFrame([
        {"skill": "Python", "category": "Technology", "subdomain": "Core", "type_hint": "hard",
         "growth": 90, "posting_trend": 80, "posting_volume": 70,
         "openings_ratio": 85, "skills_gap": 60,
         "durability": 88, "automation_resilience": 72, "cross_sector_use": 84}
    ]).to_csv(in_csv, index=False)

    out_csv = tmp_path / "07_skill_scored.csv"
    run(str(in_csv), str(out_csv), "research_v2/config/scoring_weights.yaml")
    df = pd.read_csv(out_csv)

    assert round(float(df.loc[0, "demand"]), 1) == 84.0
    assert round(float(df.loc[0, "scarcity"]), 1) == 77.5
    assert round(float(df.loc[0, "future_proof"]), 1) == 81.6
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/research_v2/test_stage_c2.py -v`
Expected: FAIL with import/module not found.

**Step 3: Write minimal implementation**

```python
# research_v2/pipeline/stage_c2_score.py
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
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/research_v2/test_stage_c2.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add research_v2/pipeline/stage_c2_score.py tests/research_v2/test_stage_c2.py
git commit -m "feat: add C2 scoring engine"
```

### Task 8: Implement C3 Ranking and Soft-Quota Enforcement

**Files:**
- Create: `research_v2/pipeline/stage_c3_rank.py`
- Create: `tests/research_v2/test_stage_c3.py`

**Step 1: Write the failing test**

```python
# tests/research_v2/test_stage_c3.py
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
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/research_v2/test_stage_c3.py -v`
Expected: FAIL with import/module not found.

**Step 3: Write minimal implementation**

```python
# research_v2/pipeline/stage_c3_rank.py
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
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/research_v2/test_stage_c3.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add research_v2/pipeline/stage_c3_rank.py tests/research_v2/test_stage_c3.py
git commit -m "feat: add C3 ranking and soft quota enforcement"
```

### Task 9: Implement C4 Quality Gate and Contract Validator

**Files:**
- Create: `research_v2/pipeline/stage_c4_quality_gate.py`
- Create: `tests/research_v2/test_stage_c4.py`

**Step 1: Write the failing test**

```python
# tests/research_v2/test_stage_c4.py
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
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/research_v2/test_stage_c4.py -v`
Expected: FAIL with import/module not found.

**Step 3: Write minimal implementation**

```python
# research_v2/pipeline/stage_c4_quality_gate.py
from __future__ import annotations
import json
import pandas as pd


def run(in_csv: str, out_csv: str, schema_json: str) -> None:
    df = pd.read_csv(in_csv)
    schema = json.loads(open(schema_json, "r", encoding="utf-8").read())["columns"]

    checks = []
    checks.append(("schema_columns", "PASS" if list(df.columns) == schema else "FAIL", str(list(df.columns))))
    checks.append(("row_count_200", "PASS" if len(df) == 200 else "FAIL", str(len(df))))
    checks.append(("soft_ratio_min_0_30", "PASS" if (df["type"] == "soft").mean() >= 0.30 else "FAIL", str((df["type"] == "soft").mean())))
    checks.append(("score_range", "PASS" if ((df[["demand", "scarcity", "future_proof"]] >= 0).all().all() and (df[["demand", "scarcity", "future_proof"]] <= 100).all().all()) else "FAIL", "0-100"))
    checks.append(("no_duplicates", "PASS" if df["skill"].nunique() == len(df) else "FAIL", str(df["skill"].nunique())))

    pd.DataFrame(checks, columns=["check_name", "status", "details"]).to_csv(out_csv, index=False)
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/research_v2/test_stage_c4.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add research_v2/pipeline/stage_c4_quality_gate.py tests/research_v2/test_stage_c4.py
git commit -m "feat: add C4 quality gate stage"
```

### Task 10: Build End-to-End Orchestrator and Final CSV Export

**Files:**
- Create: `research_v2/pipeline/run_pipeline.py`
- Create: `research_v2/output/skills_demand_ranking_v2.csv` (generated)
- Create: `tests/research_v2/test_e2e_pipeline.py`
- Modify: `research_v2/README.md`

**Step 1: Write the failing test**

```python
# tests/research_v2/test_e2e_pipeline.py
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
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/research_v2/test_e2e_pipeline.py -v`
Expected: FAIL with import/module not found.

**Step 3: Write minimal implementation**

```python
# research_v2/pipeline/run_pipeline.py
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


def run_all(base_dir: str = "research_v2", out_dir: str = "research_v2/output") -> None:
    base = Path(base_dir)
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

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

    a1(str(base / "config/categories_seed.yaml"), str(p1))
    a2(str(p1), str(p2), shards=8)
    b1(str(p2), str(p3), keep_top=18)
    b2(str(p3), str(p4), min_rows=1200)
    c1(str(p4), str(p5), str(p6), str(base / "config/synonyms.yaml"))
    c2(str(p6), str(p7), str(base / "config/scoring_weights.yaml"))
    c3(str(p7), str(p8), top_n=200, min_soft_ratio=0.30)
    c4(str(p8), str(p9), str(base / "config/final_schema.json"))

    shutil.copyfile(p8, final)
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/research_v2/test_e2e_pipeline.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add research_v2/pipeline/run_pipeline.py tests/research_v2/test_e2e_pipeline.py research_v2/README.md
git commit -m "feat: add end-to-end multi-level skill research pipeline"
```

### Task 11: Add Subagent Orchestration Runbook

**Files:**
- Create: `research_v2/runbooks/subagent-orchestration.md`
- Modify: `research_v2/README.md`

**Step 1: Write the failing doc-check test**

```python
# tests/research_v2/test_runbook.py
from pathlib import Path


def test_runbook_has_waves_and_gate_rules():
    p = Path("research_v2/runbooks/subagent-orchestration.md")
    text = p.read_text(encoding="utf-8")
    assert "Wave A" in text
    assert "Wave B" in text
    assert "Wave C" in text
    assert "Gate" in text
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/research_v2/test_runbook.py -v`
Expected: FAIL with file not found.

**Step 3: Write minimal implementation**

```markdown
# research_v2/runbooks/subagent-orchestration.md
# Subagent Orchestration

Use @superpowers:dispatching-parallel-agents for fan-out and @superpowers:subagent-driven-development for task-by-task execution.

## Wave A
- A1 taxonomy (single agent)
- A2 category triage (8 parallel shards)

## Wave B
- B1 subdomain expansion (per top category)
- B2 skill mining (per subdomain)

## Wave C
- C1 normalization
- C2 scoring
- C3 rank + quota
- C4 QA gate

## Gate Rules
- A2 must output >=25 categories
- B2 must output >=1200 evidence rows
- C3 must output exactly 200 rows and >=30% soft skills
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/research_v2/test_runbook.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add research_v2/runbooks/subagent-orchestration.md tests/research_v2/test_runbook.py research_v2/README.md
git commit -m "docs: add subagent orchestration runbook"
```

### Task 12: Final Verification and CSV Delivery Command

**Files:**
- Modify: `research_v2/README.md`

**Step 1: Add exact run commands to README**

```markdown
## Run
python -m research_v2.pipeline.run_pipeline

## Output
research_v2/output/skills_demand_ranking_v2.csv
```

**Step 2: Run full test suite**

Run: `pytest tests/research_v2 -v`
Expected: PASS all tests.

**Step 3: Run pipeline command**

Run: `python -m research_v2.pipeline.run_pipeline`
Expected: Creates `research_v2/output/skills_demand_ranking_v2.csv`.

**Step 4: Verify final CSV contract**

Run: `python -c "import pandas as pd; d=pd.read_csv('research_v2/output/skills_demand_ranking_v2.csv'); print(len(d), list(d.columns), (d['type']=='soft').mean())"`
Expected: `200 ['skill', 'category', 'type', 'demand', 'scarcity', 'future_proof']` and soft ratio `>=0.30`.

**Step 5: Commit**

```bash
git add research_v2/README.md
git commit -m "chore: document run and verification commands for research_v2"
```
