"""Request and response models for the underwriting API."""

from typing import Literal

from pydantic import BaseModel, Field, model_validator

Condition = Literal["excellent", "good", "fair", "rough", "unknown"]
TitleStatus = Literal["clean", "salvage", "rebuilt", "unknown"]
Channel = Literal["auction", "private", "dealer", "unknown"]
Desirability = Literal["HOT", "WARM", "COLD"]
RiskLevel = Literal["LOW", "MEDIUM", "HIGH"]
Verdict = Literal["BUY", "PASS", "WATCH"]


class UnderwriteRequest(BaseModel):
    vin: str | None = None
    year: int | None = None
    make: str | None = None
    model: str | None = None
    trim: str | None = "unspecified"
    engine: str | None = "unspecified"
    drivetrain: str | None = "unspecified"
    transmission: str | None = "unspecified"
    miles: int | None = None
    condition: Condition = "unknown"
    title: TitleStatus = "unknown"
    channel: Channel = "unknown"
    known_mechanical_issues: list[str] = Field(default_factory=list)
    known_cosmetic_issues: list[str] = Field(default_factory=list)
    unseen_risk: bool = False
    market_72hr_value: int | None = None
    kbb_private_party: int | None = None
    kbb_trade_in: int | None = None
    current_auction_bid: int | None = Field(
        default=None,
        description="Accepted for display only. Never used in Max Buy math.",
    )

    @model_validator(mode="after")
    def normalize_unspecified_text(self):
        for field_name in ["trim", "engine", "drivetrain", "transmission"]:
            value = getattr(self, field_name)
            if value is None or str(value).strip() == "":
                setattr(self, field_name, "unspecified")
        return self


class VehicleSummary(BaseModel):
    vin: str | None
    year: int | None
    make: str | None
    model: str | None
    trim: str
    engine: str
    miles: int | None
    condition: Condition
    title: TitleStatus
    channel: Channel


class MarketSnapshot(BaseModel):
    market_area: str
    market_72hr_value: int | None
    kbb_private_party: int | None
    kbb_trade_in: int | None
    desirability: Desirability
    confidence: Literal["low", "medium", "high"]
    notes: list[str]


class ReconReserve(BaseModel):
    best: int
    likely: int
    worst: int
    confidence: Literal["low", "medium", "high"]
    notes: list[str]


class DealMath(BaseModel):
    market_72hr_value: int | None
    recon_used: int
    profit_floor: int
    max_buy: int | None
    safe_buy_zone: str
    notes: list[str]


class AuctionCompare(BaseModel):
    current_auction_bid: int | None
    used_in_math: bool
    notes: list[str]


class UnderwriteResponse(BaseModel):
    vehicle_summary: VehicleSummary
    sacramento_market_snapshot: MarketSnapshot
    recon_reserve: ReconReserve
    deal_math: DealMath
    auction_compare: AuctionCompare
    verdict: Verdict
    risk_level: RiskLevel
    reasoning: list[str]
