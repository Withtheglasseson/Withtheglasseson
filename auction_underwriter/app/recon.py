"""SAU recon reserve logic.

Recon is one reserve expressed as Best / Most-Likely / Worst. It protects the
buy price. It does not claim the vehicle needs a repair unless evidence proves it.
"""

from app.models import PlatformIssue, ReconReserve, RepairTimeEstimate, UnderwriteRequest
from app.rulebook import BLIND_RISK_ADDERS


def _all_issue_text(request: UnderwriteRequest) -> str:
    parts = []
    parts.extend(request.known_mechanical_issues)
    parts.extend(request.known_cosmetic_issues)
    parts.extend(request.listing_notes)
    parts.extend(request.dtc_codes)
    return " ".join(parts).lower()


def _repair_time(best: int, most_likely: int, worst: int) -> RepairTimeEstimate:
    def bucket(amount: int) -> str:
        if amount <= 500:
            return "0.5-2"
        if amount <= 1500:
            return "2-6"
        if amount <= 3500:
            return "6-14"
        return "14-30+"

    return RepairTimeEstimate(
        best_hours=bucket(best),
        most_likely_hours=bucket(most_likely),
        worst_hours=bucket(worst),
    )


def _platform_patterns(request: UnderwriteRequest) -> list[PlatformIssue]:
    """Return broad pattern scan items without saying this car needs repairs."""
    make = (request.make or "").lower()
    model = (request.model or "").lower()
    miles = request.miles or 0
    issues: list[PlatformIssue] = []

    if miles >= 120_000:
        issues.append(
            PlatformIssue(
                label="🟢 nuisance",
                issue="Mileage-based wear items such as brakes, tires, fluids, mounts, and suspension checks become more likely.",
                evidence_tag="[MILES]",
                resale_risk="Usually manageable for 72-hour resale if drivability is clean.",
            )
        )

    if miles >= 180_000:
        issues.append(
            PlatformIssue(
                label="🟡 drivability",
                issue="High-mileage drivability reserve is appropriate even with no confirmed defect.",
                evidence_tag="[MILES]",
                resale_risk="May narrow buyer pool and increase test-drive scrutiny.",
            )
        )

    if "prius" in model:
        issues.append(
            PlatformIssue(
                label="🔴 catastrophic",
                issue="Hybrid battery and head-gasket risk are known platform concerns at higher mileage.",
                evidence_tag="[PATTERN]",
                resale_risk="Can become a deal-breaker if symptoms or codes are present.",
            )
        )

    if make in {"bmw", "mercedes", "mercedes-benz", "audi", "land rover", "jaguar", "mini"}:
        issues.append(
            PlatformIssue(
                label="🔴 catastrophic",
                issue="Luxury/Euro platforms carry higher diagnostic and major-repair exposure.",
                evidence_tag="[PATTERN]",
                resale_risk="Higher comeback risk; buyer pool is thinner.",
            )
        )

    if "cvt" in (request.transmission or "").lower():
        issues.append(
            PlatformIssue(
                label="🔴 catastrophic",
                issue="CVT reputation creates transmission-behavior risk allowance.",
                evidence_tag="[PATTERN]",
                resale_risk="Can materially impact buyer confidence and wholesale downside.",
            )
        )

    return issues


def estimate_recon(request: UnderwriteRequest) -> ReconReserve:
    """Estimate Best / Most-Likely / Worst recon reserves.

    Most-Likely is the only number used for Max Buy math.
    """
    condition = request.condition or "unknown"
    notes: list[str] = ["Recon is a reserve, not a claim that parts need replacement."]

    if condition == "good":
        best, most_likely, worst = 250, 600, 1200
        notes.append("Good condition uses normal light-recon reserve.")
    elif condition == "fair":
        best, most_likely, worst = 600, 1200, 2500
        notes.append("Fair condition increases reserve for cosmetic/mechanical unknowns.")
    elif condition == "rough":
        best, most_likely, worst = 1200, 2500, 5000
        notes.append("Rough condition creates high recon exposure.")
    else:
        best, most_likely, worst = 700, 1500, 3500
        notes.append("Unknown condition widens reserve.")

    issue_text = _all_issue_text(request)
    platform_scan = _platform_patterns(request)

    if request.known_mechanical_issues:
        add = 750 * len(request.known_mechanical_issues)
        most_likely += add
        worst += add * 2
        notes.append("[USER] Known mechanical issue text added as reserve allowance.")

    if request.known_cosmetic_issues:
        add = 200 * len(request.known_cosmetic_issues)
        most_likely += add
        worst += add * 2
        notes.append("[USER]/[VISIBLE] Known cosmetic issue text added as reserve allowance.")

    # Blind/unseen risk adders: apply only when appropriate and phrase as reserves.
    if request.channel == "auction" and request.unseen_risk is True:
        adder = BLIND_RISK_ADDERS["unknown_maintenance"]
        most_likely += adder["most_likely"]
        worst += adder["worst"]
        notes.append("Auction unseen risk ON: unknown maintenance/no-records reserve added.")

    keyword_adders = [
        (("undercarriage", "curb", "hit"), "undercarriage_hit", "Undercarriage/curb-strike suspicion reserve added."),
        (("oil leak", "seep", "leaking oil"), "oil_leak", "Oil leak/seep reserve added."),
        (("coolant", "overheat", "stain", "low coolant"), "cooling_system", "Cooling-system reserve added."),
        (("rough idle", "misfire", "p0300", "p0301", "p0302", "p0303", "p0304"), "rough_idle_misfire", "Rough idle/misfire reserve added."),
        (("trans", "transmission", "cvt", "slip", "jerk"), "transmission_unknown", "Transmission behavior reserve added."),
        (("abs", "traction", "vsc", "brake light", "dash light"), "dash_lights", "ABS/traction/dash-light reserve added."),
        (("a/c", "ac ", "air conditioning"), "ac_unknown", "A/C unknown reserve added."),
        (("electrical", "window", "lock", "radio", "cluster"), "interior_electrical", "Interior electrical weirdness reserve added."),
    ]

    for keywords, key, note in keyword_adders:
        if any(keyword in issue_text for keyword in keywords):
            adder = BLIND_RISK_ADDERS[key]
            most_likely += adder["most_likely"]
            worst += adder["worst"]
            notes.append(note)

    if request.title in {"salvage", "rebuilt", "unknown"}:
        most_likely += 750
        worst += 1500
        notes.append("Title friction reserve added for salvage/rebuilt/unknown title.")

    evidence_strength = 0
    if request.vin:
        evidence_strength += 1
    if request.listing_link or request.photos_provided or request.listing_notes:
        evidence_strength += 1
    if request.known_mechanical_issues or request.known_cosmetic_issues or request.dtc_codes:
        evidence_strength += 1
    if request.unseen_risk is False:
        evidence_strength += 1

    if request.unseen_risk is True:
        confidence = "Medium - auction/unseen risk caps confidence even when patterns are clear."
    elif evidence_strength >= 3:
        confidence = "85% - strong evidence for Most-Likely reserve."
    elif evidence_strength == 2:
        confidence = "70% - moderate evidence for Most-Likely reserve."
    else:
        confidence = "Low - limited evidence; reserve widened instead of guessing."

    return ReconReserve(
        best=max(best, 0),
        most_likely=max(most_likely, best),
        worst=max(worst, most_likely),
        confidence=confidence,
        repair_time=_repair_time(best, most_likely, worst),
        platform_risk_scan=platform_scan,
        notes=notes,
    )
