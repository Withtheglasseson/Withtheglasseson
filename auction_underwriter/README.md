# Sacramento Auction Underwriter

A FastAPI MVP for underwriting used vehicles for a fast Sacramento flip.

## Purpose

The app answers one core question:

> What is the most I should pay for this car and still protect profit?

## Current Version

Version `0.3.0` adds hybrid stability storage.

The app now supports:

1. `STOP` response when a required gate is missing.
2. Completed A-F underwriting response when all hard gates pass.
3. Saved underwrite records in local SQLite.

## Hybrid Stability Rule

Do not rely on AI memory for business-critical behavior.

Stable behavior must live in:

- Python code
- Versioned rulebook files
- Tests
- SQLite/database records
- Git commits

AI can help explain, summarize, and structure messy inputs, but deterministic code owns gates, formulas, verdict rules, and saved decision records.

See `docs/HYBRID_STABILITY_ARCHITECTURE.md`.

## Locked Rules

- Market: Sacramento ZIP 95835
- Radius: 75 miles
- Flip goal: 72 hours
- Profit floor: $2,000
- Max Buy uses Most-Likely Recon only
- Recon is one thing shown as Best / Most-Likely / Worst
- Current bid/ask is not used to create value or Max Buy
- Current bid/ask is only used for final BUY / PASS / PENDING comparison
- Unknown vehicle details stay unknown instead of being invented
- No fake source claims
- No repair “needs” unless evidence supports it
- Repair time is context only and does not change recon dollars

## Gate System

The app checks gates before market, recon, or deal math.

Gate order:

1. VIN preferred. If no VIN: Year / Make / Model.
2. Specs: Trim / Engine / Drivetrain / Transmission / Body style.
3. Miles.
4. Condition + title.
5. Channel: auction or private.
6. Damage/Risk Gate: known issues/listing notes OR unseen risk ON/OFF.
7. Current bid/ask, optional. If missing, verdict is PENDING.
8. DTC codes, optional.

If a required gate is missing, the app asks for only the next missing item.

## Formula

```text
Max Buy = Sacramento 72-hour private party value - most-likely recon reserve - $2,000 profit floor
```

## Local Development

```bash
cd auction_underwriter
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open:

```text
http://127.0.0.1:8000/health
http://127.0.0.1:8000/rulebook
http://127.0.0.1:8000/docs
```

## API Endpoints

```text
GET  /health
GET  /rulebook
POST /underwrite
POST /underwrite/save
GET  /runs
GET  /runs/{run_id}
```

Use `/underwrite` for temporary testing.

Use `/underwrite/save` when you want the decision recorded in SQLite.

## Smoke Test

After the API is running, open a second terminal and run:

```bash
cd auction_underwriter
python scripts/smoke_test.py
```

This checks:

- `/health` returns OK
- `/rulebook` returns the versioned rulebook
- missing specs stop at Gate 2
- completed Corolla example returns A-F with BUY and Max Buy
- `/underwrite/save` saves a record
- `/runs` lists saved records
- `/runs/{run_id}` returns the full saved request and response

## Example STOP Request

POST to `/underwrite` with missing specs:

```json
{
  "year": 2008,
  "make": "Toyota",
  "model": "Corolla"
}
```

Expected behavior:

```text
STOP at Gate 2 and ask for trim only.
```

## Example Completed Request

POST to `/underwrite` or `/underwrite/save`:

```json
{
  "mode": "FULL_UNDERWRITE",
  "year": 2008,
  "make": "Toyota",
  "model": "Corolla",
  "trim": "CE/LE/S",
  "engine": "unspecified",
  "drivetrain": "FWD",
  "transmission": "automatic",
  "body_style": "sedan",
  "miles": 150000,
  "condition": "good",
  "title": "clean",
  "channel": "auction",
  "known_mechanical_issues": [],
  "known_cosmetic_issues": ["roof rust"],
  "listing_notes": [],
  "unseen_risk": false,
  "market_72hr_value": 6500,
  "current_bid_or_ask": 1600
}
```

Expected result:

```text
A-F underwriting response with Max Buy, recon reserve, market snapshot, auction compare, and BUY/PASS/PENDING verdict.
```

## Current Status

This is still a connected MVP skeleton. Real external data integrations are intentionally not wired yet.

Already real code:

- Gatekeeper
- Rulebook constants
- Request/response models
- Max Buy math
- Recon reserve structure
- Market desirability scoring
- Verdict comparison
- SQLite saved runs
- Smoke test

Stubbed for later:

- VIN decode
- KBB lookup
- Sacramento listing search
- Auction comparison
- Photo/risk detection
- DealerCenter integration

See `SAU_MASTER_RULES.md` for the full copy/paste master ruleset.
