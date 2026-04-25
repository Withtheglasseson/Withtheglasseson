"""FastAPI entrypoint for Sacramento Auction Underwriter."""

from typing import Any, Union

from fastapi import FastAPI, HTTPException

from app.models import GateStopResponse, UnderwriteRequest, UnderwriteResponse
from app.rulebook import get_rulebook
from app.storage import get_underwrite_run, init_db, list_underwrite_runs, save_underwrite_run
from app.underwriter import underwrite_vehicle

app = FastAPI(
    title="Sacramento Auction Underwriter",
    description="72-hour flip underwriting engine for used-car auction decisions.",
    version="0.3.0",
)


@app.on_event("startup")
def startup() -> None:
    init_db()


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "auction_underwriter", "version": "0.3.0"}


@app.get("/rulebook")
def rulebook() -> dict:
    return get_rulebook()


@app.post("/underwrite", response_model=Union[UnderwriteResponse, GateStopResponse])
def underwrite(request: UnderwriteRequest) -> UnderwriteResponse | GateStopResponse:
    return underwrite_vehicle(request)


@app.post("/underwrite/save")
def underwrite_and_save(request: UnderwriteRequest) -> dict[str, Any]:
    response = underwrite_vehicle(request)
    run_id = save_underwrite_run(request, response)
    return {
        "saved": True,
        "run_id": run_id,
        "response": response,
    }


@app.get("/runs")
def runs(limit: int = 25) -> list[dict[str, Any]]:
    return list_underwrite_runs(limit=limit)


@app.get("/runs/{run_id}")
def run_detail(run_id: int) -> dict[str, Any]:
    run = get_underwrite_run(run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Underwrite run not found")
    return run
