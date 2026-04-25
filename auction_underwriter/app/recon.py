"""Recon reserve logic.

This module creates reserves, not accusations. A reserve protects the buy price
against likely costs and risk.
"""

from app.models import ReconReserve, UnderwriteRequest


def estimate_recon(request: UnderwriteRequest) -> ReconReserve:
    """Estimate best/likely/worst recon reserves from known inputs.

    MVP logic is intentionally conservative and simple. Later, this can be
    replaced with make/model-specific rules and photo/code parsing.
    """
    best = 250
    likely = 500
    worst = 1000
    notes: list[str] = ["MVP baseline reserve applied."]
    confidence = "medium"

    if request.condition == "excellent":
        best, likely, worst = 150, 350, 750
        notes.append("Excellent condition lowers baseline reserve.")
    elif request.condition == "good":
        best, likely, worst = 250, 600, 1200
        notes.append("Good condition uses normal light-recon reserve.")
    elif request.condition == "fair":
        best, likely, worst = 600, 1200, 2500
        notes.append("Fair condition increases recon reserve.")
    elif request.condition == "rough":
        best, likely, worst = 1200, 2500, 5000
        notes.append("Rough condition creates high recon exposure.")
    else:
        best, likely, worst = 700, 1500, 3500
        confidence = "low"
        notes.append("Unknown condition widens reserve and lowers confidence.")

    if request.known_mechanical_issues:
        add = 750 * len(request.known_mechanical_issues)
        likely += add
        worst += add * 2
        notes.append("Known mechanical issues added to likely and worst reserves.")

    if request.known_cosmetic_issues:
        add = 200 * len(request.known_cosmetic_issues)
        likely += add
        worst += add * 2
        notes.append("Known cosmetic issues added as reconditioning reserve.")

    if request.unseen_risk:
        likely += 500
        worst += 1500
        confidence = "low" if confidence == "medium" else confidence
        notes.append("Unseen auction risk is ON, so reserve is widened.")
    else:
        notes.append("Unseen auction risk is OFF based on user input.")

    if request.title != "clean":
        likely += 750
        worst += 1500
        notes.append("Non-clean or unknown title increases market/recon risk reserve.")

    return ReconReserve(
        best=max(best, 0),
        likely=max(likely, best),
        worst=max(worst, likely),
        confidence=confidence,
        notes=notes,
    )
