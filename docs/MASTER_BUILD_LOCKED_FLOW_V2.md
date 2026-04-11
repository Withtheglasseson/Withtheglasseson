# VIN Scan App — Master Build (Locked Flow V2)

## Core Objective
Buy right → Fix right → Sell fast → Profit.

## Locked App Flow (Do Not Change)
1. VIN
2. IDENTITY
3. MECHANICAL PROBLEM HISTORY
4. MARKET
5. AUCTION
6. ALIGNMENT
7. RECON
8. DEAL MATH
9. MARKETABILITY CHECK

## Hard Rules
- No cosmetic analysis in Phase 2.
- No pricing before Market phase.
- No decision before Recon.
- Auction supports entry, not decision.
- Market defines sell reality.

## Final Decision Logic
- `PROFIT = SELL PRICE - (BUY + RECON + FEES)`
- `TOTAL COST = BUY + RECON + FEES`

Decision policy:
- BUY if `profit >= 2000` and marketability is FAST (`<= 10 days`).
- WATCH if `profit >= 1200` and marketability is NORMAL (`10–20 days`).
- PASS otherwise.

## Phase Outputs Summary
- VIN + IDENTITY: VIN decode and full vehicle confirmation.
- Mechanical History: issue list, severity, mileage range, inspection checklist, risk summary.
- Market: move value, DOM, velocity, listing count, saturation, price drops.
- Auction: low/avg/high, 7-day trend, 30-day trend, volume, dealer activity.
- Alignment: confirmed / mismatch / opportunity.
- Recon: recon estimate, damage flags, risk level.
- Deal Math: total cost and profit projection.
- Marketability: FAST / NORMAL / SLOW and final BUY/WATCH/PASS action.

## System Truth
- Auction → what dealers believe.
- Market → what actually sells.
- Recon → what it costs.
- Marketability → whether you get paid.
