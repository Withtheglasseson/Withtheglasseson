# Hybrid Stability Architecture

## Core Principle

Do not depend on AI memory for business-critical behavior.

The stable source of truth must live in the codebase and data layer:

1. Deterministic Python code
2. Versioned rulebook files
3. Tests
4. Saved inputs/outputs in a database
5. Optional AI layer for explanation, summarization, and flexible research

AI can assist, but it should not be trusted as the only place where rules live.

## Why Hybrid

The app needs two kinds of intelligence:

### 1. Stable Code Brain

This is the part that must be consistent every time.

Owned by real code:

- Gate order
- Hard stops
- Required fields
- Missing-item prompts
- Max Buy formula
- Profit floor
- Verdict rules
- Recon math structure
- Desirability scoring rules
- Input/output schemas
- Tests
- Database records

If this part changes, it should change through a code commit.

### 2. Flexible AI Layer

This part can be handled by an LLM later, but only inside boundaries.

Allowed AI jobs:

- Explain the result in plain English
- Summarize listing notes
- Summarize photos when image input is available
- Convert messy user text into structured fields
- Draft customer-facing descriptions
- Help compare live market sources when browsing/data connectors exist
- Suggest possible platform risks with evidence labels

Forbidden AI jobs:

- Changing locked constants
- Skipping gates
- Inventing missing trim/engine/drivetrain/transmission
- Creating Max Buy formula dynamically
- Compressing profit floor
- Using auction bid to create value
- Claiming sources were checked when they were not checked
- Saying parts need replacement without evidence

## Practical Architecture

```text
User / UI
   ↓
Input Normalizer
   ↓
Gatekeeper             ← deterministic code
   ↓
Market Module          ← deterministic first; live data later
   ↓
Recon Module           ← deterministic reserve logic
   ↓
Deal Math              ← deterministic formula
   ↓
Verdict Engine         ← deterministic rules
   ↓
AI Explanation Layer   ← optional helper only
   ↓
Saved Deal Record      ← database later
```

## Current MVP Status

Already deterministic:

- Gatekeeper
- Rulebook constants
- Request/response models
- Max Buy math
- Recon reserve structure
- Market desirability scoring
- Verdict comparison
- Smoke test

Still stubbed:

- VIN decode
- KBB lookup
- Sacramento market listings
- Auction comparison
- Photo/risk detection
- DealerCenter integration
- Database persistence

## Stability Rule

If a rule matters, it must exist in at least one of these places:

- Python code
- Markdown rulebook in repo
- Test file
- Database migration/schema

If it only exists in a chat message, it is not stable.

## Next Engineering Target

Add persistent deal storage:

- SQLite for local MVP
- Save every underwrite request
- Save every underwrite response
- Save rulebook version used
- Save timestamp
- Save verdict and Max Buy

This allows repeatable audits and prevents the app from becoming random AI soup.

## Summary

The app is hybrid, but code is the boss.

AI helps read, explain, and organize.

Python enforces the rules and makes the same decision the same way every time.
