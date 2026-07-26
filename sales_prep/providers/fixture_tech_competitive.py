from typing import Any

from ._fixture_utils import load_fixture_file, load_generic_template, render_placeholder


class FixtureTechCompetitiveProvider:
    def search(self, domain: str, company_name: str) -> dict[str, Any]:
        data = load_fixture_file("tech_competitive.json")
        if domain in data:
            return {**data[domain], "is_demo_fallback": False}
        template = load_generic_template()["tech_competitive"]
        return {**render_placeholder(template, company_name), "is_demo_fallback": True}
