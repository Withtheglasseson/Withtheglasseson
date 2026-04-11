# Versioning Approach for This Build

Short answer: **yes, versions should be progressive improvements**, not random alternative ideas.

## What a "new version" means here
A new version (v2, v3, etc.) should be:

1. Backward-consistent with locked rules (phase order + decision policy).
2. Strictly better in at least one measurable way (clarity, test coverage, robustness, speed, maintainability).
3. Non-regressive (it should not re-open solved behavior unless explicitly requested).

## What a version is **not**
A new version is not just a stylistic rewrite with different assumptions.
If assumptions change (for example `move_value` derivation), that must be explicitly called out as a product-policy update.

## Practical policy for this repo
When proposing v(n+1):

- Keep all locked-flow constraints.
- Keep prior passing behavior unless the user asks for policy change.
- Add tests for any changed behavior.
- Document exactly what improved and why it is better.

## Decision rule
If two versions both pass tests, pick the one with:

- higher spec fidelity,
- less ambiguity,
- simpler reasoning path,
- and stronger failure handling.

That means v2 should generally dominate v1 unless requirements changed.
