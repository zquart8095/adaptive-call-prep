"""Provider adapters — one Protocol per data-source type. Swapping a fixture
implementation for a real vendor integration never touches pipeline/graph.py;
that's the whole point of the seam."""

from typing import Any, Protocol


class CompanySnapshotProvider(Protocol):
    def fetch(self, domain: str, company_name: str) -> dict[str, Any]: ...


class SignalsProvider(Protocol):
    def search(self, domain: str, company_name: str, since_days: int = 180) -> list[dict[str, Any]]: ...


class StakeholderProvider(Protocol):
    def search(
        self, domain: str, company_name: str, target_names: list[str]
    ) -> list[dict[str, Any]]: ...


class TechCompetitiveProvider(Protocol):
    def search(self, domain: str, company_name: str) -> dict[str, Any]: ...
