from pathlib import Path


def test_runbook_has_waves_and_gate_rules():
    p = Path("research_v2/runbooks/subagent-orchestration.md")
    text = p.read_text(encoding="utf-8")
    assert "Wave A" in text
    assert "Wave B" in text
    assert "Wave C" in text
    assert "Gate" in text
