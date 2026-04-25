"""Request and response models for the underwriting API."""

from typing import Literal

from pydantic import BaseModel, Field, model_validator

Mode = Literal["DEEP_SEARCH", "QUICK", "MARKET_ONLY", "FULL_UNDERWRITE"]
Condition = Literal["good", "fair", "rough", "unknown"]
TitleStatus = Literal["clean", "salvage", "rebuilt", "unknown"]
Channel = Literal["auction", "private"]
DesirabilityLabel = Literal["HOT", "WARM", "COLD"]
RiskLevel = Literal["LOW", "MEDIUM", "HIGH"]
Verdict = Literal["BUY", "PASS", "PENDING"]
GateStatus = Literal["STOP", "PASSED"]


class UnderwriteRequest(BaseModel):
    """Incoming vehicle data.

    None means the app has not received the answer yet.
    The literal string "unspecified" means the user intentionally chose unknown.
    """

    mode: Mode = "DEEP_SEARCH"
    vin: str | None = None
    listing_link: str | None = None
    photos_provided: bool = False

    year: int | None = None
    make: str | None = None
    model: str | None = None
    trim: str | None = None
    engine: str | None = None
    drivetrain: str | None = None
    transmission: str | None = None
    body_style: str | None = None

    miles: int | None = None
    condition: Condition | None = None
    title: TitleStatus | None = None
    channel: Channel | None = None

    known_mechanical_issues: list[str] = Field(default_factory=list)
    known_cosmetic_issues: list[str] = Field(default_factory=list)
    listing_notes: list[str] = Field(default_factory=list)
    unseen_risk: bool | None = Field(
        default=None,
        description="Damage/Risk Gate answer. True = unseen risk ON, False = unseen risk OFF, None = unanswered.",
    )

    current_bid_or_ask: int | None = None
    auction_average: int | None = None
    dtc_codes: list[str] = Field(default_factory=list)

    market_72hr_value: int | None = None
    kbb_private_party: int | None = None
    kbb_trade_in: int | None = None

    @model_validator(mode="after")
    def normalize_text_fields(self):
        text_fields = [
            "vin",
            "listing_link",
            "make",
            "model",
            "trim",
            "engine",
            "drivetrain",
            "transmission",
            "body_style",
        ]
        for field_name in text_fields:
            value = getattr(self, field_name)
            if isinstance(value, str) and value.strip() == "":
                setattr(self, field_name, None)
            elif isinstance(value, str):
                setattr(self, field_name, value.strip())
        return self


class GateStopResponse(BaseModel):
    status: GateStatus = "STOP"
    gate: str
    missing_field: str
    question: str
    received_so_far: dict
    rule: str


class VehicleSummary(BaseModel):
    vin: str | None
    year: int | None
    make: str | None
    model: str | None
    trim: str
    engine: str
    drivetrain: str
    transmission: str
    body_style: str
    miles: int | None
    condition: str
    title: str
    channel: str


class MarketSnapshot(BaseModel):
    market_area: str
    mode: Mode
    market_72hr_value: int | None
    value_label: str
    kbb_private_party: int | None
    kbb_trade_in: int | None
    desirability_score: int
    desirability_label: DesirabilityLabel
    reliability_score: int
    market_premium_vs_book: str
    confidence: Literal["low", "medium", "high"]
    notes: list[str]


class PlatformIssue(BaseModel):
    label: Literal["🟢 nuisance", "🟡 drivability", "🔴 catastrophic"]
    issue: str
    evidence_tag: Literal["[USER]", "[CODE]", "[VISIBLE]", "[MILES]", "[PATTERN]"]
    resale_risk: str


class RepairTimeEstimate(BaseModel):
    best_hours: str
    most_likely_hours: str
    worst_hours: str
    note: str = "Context only. Does not change recon dollars."


class ReconReserve(BaseModel):
    best: int
    most_likely: int
    worst: int
    confidence: str
    repair_time: RepairTimeEstimate
    platform_risk_scan: list[PlatformIssue]
    notes: list[str]


class DealMath(BaseModel):
    market_72hr_value: int | None
    recon_used: int | None
    profit_floor: int
    max_buy: int | None
    formula: str
    notes: list[str]


class AuctionCompare(BaseModel):
    current_bid_or_ask: int | None
    auction_average: int | None
    current_bid_used_in_math: bool
    auction_average_result: str
    notes: list[str]


class UnderwriteResponse(BaseModel):
    status: GateStatus = "PASSED"
    output_format: str = "A-F"
    vehicle_summary: VehicleSummary
    sacramento_market_snapshot: MarketSnapshot
    recon_mechanical: ReconReserve | None = None
    deal_math: DealMath | None = None
    auction_compare: AuctionCompare | None = None
    verdict: Verdict | None = None
    risk_level: RiskLevel | None = None
    reasoning: list[str]
    sources_checked_today: list[str] | None = None
