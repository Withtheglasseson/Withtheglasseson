"""FastAPI entrypoint for Sacramento Auction Underwriter."""

from fastapi import FastAPI

from app.models import UnderwriteRequest, UnderwriteResponse
from app.rulebook import get_rulebook
from app.underwriter import underwrite_vehicle

app = FastAPI(
    title="Sacramento Auction Underwriter",
    description="72-hour flip underwriting engine for used-car auction decisions.",
    version="0.1.0",
)


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "auction_underwriter"}


@app.get("/rulebook")
def rulebook() -> dict:
    return get_rulebook()


@app.post("/underwrite", response_model=UnderwriteResponse)
def underwrite(request: UnderwriteRequest) -> UnderwriteResponse:
    return underwrite_vehicle(request)
