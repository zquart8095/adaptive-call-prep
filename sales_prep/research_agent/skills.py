"""Maps the plan's skill_hints strings onto the same fixture providers the
fixed pipeline uses — no new data source, just a different entry point
(plan-driven, only the skills a goal actually calls for, not always-run-
all-four)."""

from typing import Any, Callable

from sales_prep.config import CallContext
from sales_prep.providers.fixture_company_snapshot import FixtureCompanySnapshotProvider
from sales_prep.providers.fixture_signals import FixtureSignalsProvider
from sales_prep.providers.fixture_stakeholders import FixtureStakeholderProvider
from sales_prep.providers.fixture_tech_competitive import FixtureTechCompetitiveProvider

_snapshot_provider = FixtureCompanySnapshotProvider()
_signals_provider = FixtureSignalsProvider()
_stakeholder_provider = FixtureStakeholderProvider()
_tech_provider = FixtureTechCompetitiveProvider()


def fetch_company_snapshot(context: CallContext) -> Any:
    return _snapshot_provider.fetch(context.prospect_domain, context.prospect_company)


def fetch_signals(context: CallContext) -> Any:
    return _signals_provider.search(context.prospect_domain, context.prospect_company)


def fetch_stakeholders(context: CallContext) -> Any:
    return _stakeholder_provider.search(
        context.prospect_domain, context.prospect_company, context.target_stakeholders
    )


def fetch_tech_competitive(context: CallContext) -> Any:
    return _tech_provider.search(context.prospect_domain, context.prospect_company)


SKILL_FETCHERS: dict[str, Callable[[CallContext], Any]] = {
    "company_snapshot": fetch_company_snapshot,
    "signals": fetch_signals,
    "stakeholders": fetch_stakeholders,
    "tech_competitive": fetch_tech_competitive,
}


def is_fallback_result(raw: Any) -> bool:
    """Fixture results are either a single dict (snapshot/tech_competitive)
    or a list of dicts (signals/stakeholders) — each carries its own
    is_demo_fallback flag."""
    if isinstance(raw, list):
        return any(item.get("is_demo_fallback") for item in raw)
    return bool(raw.get("is_demo_fallback"))
