from __future__ import annotations
import os
import json
from pathlib import Path
from repo_mesh.contracts import EvidenceItem
from repo_mesh.skill_index import load_skill_index, Skill

_EXTENSIONS = {".md", ".py", ".ts", ".tsx", ".js", ".txt", ".ipynb", ".yaml", ".yml"}
_MAX_CHARS_PER_FILE = 3000
_MAX_TOTAL_CHARS = 15000

TOOL_DEF = {
    "name": "record_skill_evidence",
    "description": "Record a skill detected in the repository content.",
    "input_schema": {
        "type": "object",
        "properties": {
            "skill_name": {
                "type": "string",
                "description": "The exact skill name from the provided list"
            },
            "signal_type": {
                "type": "string",
                "enum": ["functionality", "intention", "interest"],
                "description": "functionality=skill is implemented/used, intention=skill the user aims to develop or apply, interest=skill the user shows curiosity about"
            },
            "summary": {
                "type": "string",
                "description": "One sentence explaining the evidence for this skill"
            },
            "confidence": {
                "type": "number",
                "description": "0.0-1.0 confidence score"
            }
        },
        "required": ["skill_name", "signal_type", "summary", "confidence"]
    }
}


def _classify_text(text: str) -> list[tuple[str, str]]:
    """Fallback keyword-based classifier used when ANTHROPIC_API_KEY is not set."""
    lowered = text.lower()
    out: list[tuple[str, str]] = []
    if any(word in lowered for word in ["help", "improve", "support", "build"]):
        out.append(("intention", "User appears focused on helping or improving outcomes"))
    if any(word in lowered for word in ["def ", "class ", "function", "api", "pipeline"]):
        out.append(("functionality", "Repository emphasizes implementation mechanics"))
    if any(word in lowered for word in ["habit", "learning", "health", "productivity", "design"]):
        out.append(("interest", "Repository signals recurring personal/professional interests"))
    return out


def _fallback_extract(repo_id: str, repo_path: str) -> list[EvidenceItem]:
    """Old keyword-based fallback for when no API key is available (e.g., in tests)."""
    root = Path(repo_path)
    items: list[EvidenceItem] = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix not in {".md", ".py", ".ts", ".tsx", ".js", ".txt"}:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")[:5000]
        for idx, (signal_type, summary) in enumerate(_classify_text(text)):
            items.append(
                EvidenceItem(
                    evidence_id=f"{repo_id}:{path.name}:{idx}",
                    repo_id=repo_id,
                    signal_type=signal_type,
                    summary=summary,
                    source_ref=str(path),
                    weight=1.0,
                )
            )
    return items


def _collect_repo_text(repo_path: str) -> str:
    root = Path(repo_path)
    parts: list[str] = []
    total = 0
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        if path.suffix not in _EXTENSIONS:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")[:_MAX_CHARS_PER_FILE]
        except Exception:
            continue
        snippet = f"=== {path.relative_to(root)} ===\n{text}\n"
        parts.append(snippet)
        total += len(snippet)
        if total >= _MAX_TOTAL_CHARS:
            break
    return "\n".join(parts)


def extract_repo_evidence(repo_id: str, repo_path: str) -> list[EvidenceItem]:
    root = Path(repo_path)
    if not root.exists():
        raise FileNotFoundError(repo_path)

    # Fallback to keyword matching if no API key is configured
    if not os.getenv("ANTHROPIC_API_KEY"):
        return _fallback_extract(repo_id, repo_path)

    import anthropic

    skills = load_skill_index()
    skill_names = [s.name for s in skills]
    skill_list_text = "\n".join(f"- {s.name} ({s.category}, {s.type})" for s in skills)

    repo_text = _collect_repo_text(repo_path)
    if not repo_text.strip():
        return []

    client = anthropic.Anthropic()

    system = (
        "You are an expert at analyzing software repositories to infer the skills, intentions, and interests "
        "of the developer. You will be given repository file contents and a list of 500 real-world skills. "
        "For each skill you detect evidence of, call record_skill_evidence exactly once. "
        "Only record skills with clear evidence. Do not hallucinate."
    )

    user = f"""Repository: {repo_id}

SKILL TAXONOMY (use exact names):
{skill_list_text}

REPOSITORY CONTENT:
{repo_text}

Analyze the repository and call record_skill_evidence for each skill you find clear evidence of."""

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=4096,
        system=system,
        tools=[TOOL_DEF],
        messages=[{"role": "user", "content": user}],
    )

    items: list[EvidenceItem] = []
    seen_skills: set[str] = set()

    for block in response.content:
        if block.type != "tool_use" or block.name != "record_skill_evidence":
            continue
        inp = block.input
        skill_name = inp.get("skill_name", "").strip()
        if not skill_name or skill_name in seen_skills:
            continue
        if skill_name not in skill_names:
            continue  # reject hallucinated skills not in taxonomy
        seen_skills.add(skill_name)

        # find metadata for this skill
        skill_meta = next((s for s in skills if s.name == skill_name), None)
        weight = round((skill_meta.demand / 100) if skill_meta else 1.0, 3)

        items.append(EvidenceItem(
            evidence_id=f"{repo_id}:{skill_name.lower().replace(' ', '_')}",
            repo_id=repo_id,
            signal_type=inp.get("signal_type", "functionality"),
            summary=f"[{skill_name}] {inp.get('summary', '')}",
            source_ref=repo_path,
            weight=weight,
        ))

    return items
