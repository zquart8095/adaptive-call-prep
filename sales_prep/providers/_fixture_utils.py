import json
from pathlib import Path
from typing import Any

_FIXTURES_DIR = Path(__file__).parent / "fixtures"


def load_fixture_file(name: str) -> dict[str, Any]:
    return json.loads((_FIXTURES_DIR / name).read_text())


def load_generic_template() -> dict[str, Any]:
    return load_fixture_file("generic_template.json")


def render_placeholder(value: Any, company_name: str, stakeholder: str = "") -> Any:
    """Recursively fills {company}/{stakeholder} placeholders in the generic
    fallback template — used whenever a domain isn't in the fixture files,
    so typing in an arbitrary company name never crashes the demo."""
    if isinstance(value, str):
        return value.format(company=company_name, stakeholder=stakeholder)
    if isinstance(value, dict):
        return {k: render_placeholder(v, company_name, stakeholder) for k, v in value.items()}
    if isinstance(value, list):
        return [render_placeholder(v, company_name, stakeholder) for v in value]
    return value
