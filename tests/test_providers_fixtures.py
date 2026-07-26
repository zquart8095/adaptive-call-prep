from sales_prep.providers.fixture_company_snapshot import FixtureCompanySnapshotProvider
from sales_prep.providers.fixture_signals import FixtureSignalsProvider
from sales_prep.providers.fixture_stakeholders import FixtureStakeholderProvider
from sales_prep.providers.fixture_tech_competitive import FixtureTechCompetitiveProvider


def test_company_snapshot_known_domain():
    raw = FixtureCompanySnapshotProvider().fetch("alderleaf-robotics.example", "Alderleaf Robotics")
    assert raw["is_demo_fallback"] is False
    assert raw["legal_name"] == "Alderleaf Robotics, Inc."


def test_company_snapshot_unknown_domain_falls_back():
    raw = FixtureCompanySnapshotProvider().fetch("nonexistent.example", "Totally Fake Co")
    assert raw["is_demo_fallback"] is True
    assert "Totally Fake Co" in raw["description"]


def test_signals_unknown_domain_falls_back():
    signals = FixtureSignalsProvider().search("nonexistent.example", "Totally Fake Co")
    assert len(signals) == 1
    assert signals[0]["is_demo_fallback"] is True


def test_stakeholders_unknown_domain_falls_back_per_name():
    stakeholders = FixtureStakeholderProvider().search(
        "nonexistent.example", "Totally Fake Co", ["Alex Rivera", "Jamie Chen"]
    )
    assert len(stakeholders) == 2
    assert {s["name"] for s in stakeholders} == {"Alex Rivera", "Jamie Chen"}
    assert all(s["is_demo_fallback"] for s in stakeholders)


def test_tech_competitive_known_domain():
    raw = FixtureTechCompetitiveProvider().search("alderleaf-robotics.example", "Alderleaf Robotics")
    assert raw["is_demo_fallback"] is False
    assert "FactoryPulse" in raw["competitors_evaluated"]
