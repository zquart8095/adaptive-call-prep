from sales_prep.config import CallContext, DealStage


def make_call_context(**overrides) -> CallContext:
    defaults = dict(
        prospect_company="Alderleaf Robotics",
        prospect_domain="alderleaf-robotics.example",
        salesperson_name="Priya Nakamura",
        vendor_product_name="Vantage Ops Suite",
        vendor_product_one_liner="Unified observability for industrial ops teams",
        deal_stage=DealStage.discovery,
        meeting_type="30-min discovery call",
        call_datetime="2026-07-29T15:00:00-07:00",
        target_stakeholders=["Jordan Ellery"],
    )
    defaults.update(overrides)
    return CallContext(**defaults)
