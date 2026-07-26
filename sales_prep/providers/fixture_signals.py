from typing import Any

from ._fixture_utils import load_fixture_file, load_generic_template, render_placeholder


class FixtureSignalsProvider:
    def search(self, domain: str, company_name: str, since_days: int = 180) -> list[dict[str, Any]]:
        data = load_fixture_file("signals.json")
        if domain in data:
            return [{**s, "is_demo_fallback": False} for s in data[domain]]
        template = load_generic_template()["signals"]
        return [{**render_placeholder(s, company_name), "is_demo_fallback": True} for s in template]
