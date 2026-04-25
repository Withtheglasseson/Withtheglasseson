"""FastAPI entrypoint for Sacramento Auction Underwriter."""

from typing import Union

from fastapi import FastAPI

from app.models import GateStopResponse, UnderwriteRequest, UnderwriteResponse
from app.rulebook import get_rulebook
from app.underwriter import underwrite_vehicle

app = FastAPI(
    title="Sacramento Auction Underwriter",
    description="72-hour flip underwriting engine for used-car auction decisions.",
    version="0.2.0",
)


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "auction_underwriter", "version": "0.2.0"}


@app.get("/rulebook")
def rulebook() -> dict:
    return get_rulebook()


@app.post("/underwrite", response_model=Union[UnderwriteResponse, GateStopResponse])
def underwrite(request: UnderwriteRequest) -> UnderwriteResponse | GateStopResponse:
    return underwrite_vehicle(request)
