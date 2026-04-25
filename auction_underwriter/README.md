# Sacramento Auction Underwriter

A FastAPI MVP for underwriting used vehicles for a fast Sacramento flip.

## Purpose

The app answers one core question:

> What is the most I should pay for this car and still protect profit?

## Locked Rules

- Market: Sacramento ZIP 95835
- Radius: 75 miles
- Flip goal: 72 hours
- Profit floor: $2,000
- Max Buy uses Most-Likely Recon only
- Current auction bid is not used in valuation math
- Unknown vehicle details stay unknown instead of being invented
- No labor-hour estimates

## Formula

```text
Max Buy = 72-hour market value - most-likely recon reserve - $2,000 profit floor
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

## Example Request

POST to `/underwrite`:

```json
{
  "year": 2008,
  "make": "Toyota",
  "model": "Corolla",
  "trim": "CE/LE/S",
  "miles": 150000,
  "condition": "good",
  "title": "clean",
  "channel": "auction",
  "known_mechanical_issues": [],
  "known_cosmetic_issues": ["roof rust"],
  "unseen_risk": false,
  "market_72hr_value": 6500,
  "current_auction_bid": 1600
}
```

## Current Status

This is the connected skeleton. Real data integrations are intentionally not wired yet.

Stubbed for later:

- VIN decode
- KBB lookup
- Sacramento listing search
- Auction comparison
- Photo/risk detection
- DealerCenter integration
