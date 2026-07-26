from typing import Any

from ._fixture_utils import load_fixture_file, load_generic_template, render_placeholder


class FixtureStakeholderProvider:
    def search(
        self, domain: str, company_name: str, target_names: list[str]
    ) -> list[dict[str, Any]]:
        data = load_fixture_file("stakeholders.json")
        if domain in data:
            return [{**s, "is_demo_fallback": False} for s in data[domain]]

        template = load_generic_template()["stakeholders"][0]
        names = target_names or ["Unknown Stakeholder"]
        return [
            {**render_placeholder(template, company_name, stakeholder=name), "is_demo_fallback": True}
            for name in names
        ]
