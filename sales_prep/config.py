from enum import Enum

from pydantic import BaseModel


class DealStage(str, Enum):
    cold_outbound = "cold_outbound"
    discovery = "discovery"
    demo_scheduled = "demo_scheduled"
    negotiation = "negotiation"


class CallContext(BaseModel):
    """Input to a pipeline run — the analog of a producer-supplied config:
    who we're calling, what we're selling, and what's already known."""

    prospect_company: str
    prospect_domain: str
    salesperson_name: str
    vendor_product_name: str
    vendor_product_one_liner: str
    deal_stage: DealStage
    meeting_type: str
    call_datetime: str
    sdr_notes: str = ""
    target_stakeholders: list[str] = []
