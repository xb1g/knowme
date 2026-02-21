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
