from sales_prep.research_agent.nodes.compose import _build_citation_registry


def test_fixture_citations_never_get_a_fabricated_url():
    sections = {
        "goal-1": {
            "goal": {"title": "Company snapshot"},
            "raw_findings": [
                {
                    "kind": "fixture",
                    "skill": "company_snapshot",
                    "payload": {"legal_name": "Alderleaf Robotics, Inc."},
                }
            ],
        }
    }
    registry = _build_citation_registry(sections)

    assert len(registry) == 1
    assert registry[0]["source_kind"] == "fixture"
    assert registry[0]["url"] is None


def test_web_search_citations_carry_a_real_url():
    sections = {
        "goal-1": {
            "goal": {"title": "Industry context"},
            "raw_findings": [
                {
                    "kind": "web_search_followup",
                    "summary": "Some summary text.",
                    "citations": [{"title": "Some Article", "url": "https://example.com/a", "page_age": "2 days ago"}],
                }
            ],
        }
    }
    registry = _build_citation_registry(sections)

    assert len(registry) == 1
    assert registry[0]["source_kind"] == "web_search"
    assert registry[0]["url"] == "https://example.com/a"
    assert "Some Article" in registry[0]["label"]


def test_citation_ids_are_stable_and_sequential_across_sections():
    sections = {
        "goal-1": {
            "goal": {"title": "Stakeholders"},
            "raw_findings": [
                {
                    "kind": "fixture",
                    "skill": "stakeholders",
                    "payload": [
                        {"name": "Jordan Ellery"},
                        {"name": "Sam Okafor"},
                    ],
                }
            ],
        },
        "goal-2": {
            "goal": {"title": "Competitive"},
            "raw_findings": [
                {
                    "kind": "fixture",
                    "skill": "tech_competitive",
                    "payload": {"competitors_evaluated": ["FactoryPulse"]},
                }
            ],
        },
    }
    registry = _build_citation_registry(sections)

    ids = [entry["citation_id"] for entry in registry]
    assert ids == ["cite-1", "cite-2", "cite-3"]
    assert "Jordan Ellery" in registry[0]["label"]
    assert "Sam Okafor" in registry[1]["label"]
    assert registry[2]["label"] == "Competitive Landscape"


def test_empty_findings_produce_empty_registry():
    sections = {"goal-1": {"goal": {"title": "Empty"}, "raw_findings": []}}
    assert _build_citation_registry(sections) == []
