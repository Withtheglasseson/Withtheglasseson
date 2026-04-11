# Choosing the Best Version (Locked Flow V2)

If two versions both "work," choose the one that is most faithful to the system purpose:

> Buy right → Fix right → Sell fast → Profit

## 1) Hard Gate (non-negotiable)
Reject any version that fails **any** of these:

1. Preserves exact phase order.
2. Preserves decision policy thresholds.
3. Keeps Market Engine outputs and thresholds exact.
4. Avoids cross-phase scope creep when task is Phase 3.

## 2) Efficiency + Purpose Scorecard
Score 0-2 in each category:

- Spec fidelity (weight x2)
- Computational simplicity (single pass or close)
- Test completeness (FAST/NORMAL/SLOW + empty input)
- Explicit assumptions (especially `move_value` derivation)
- Change isolation (minimal unrelated edits)

Formula:

`score = 2*fidelity + simplicity + tests + assumptions + isolation`

Highest score wins.

## 3) What this means for the current implementation
Current implementation should be considered strong if it:

- Uses `avg_dom` thresholds exactly (`<=10 FAST`, `<=20 NORMAL`, else `SLOW`)
- Computes outputs only from listing `price` and `days`
- Raises on empty input so bad data does not silently pass
- Has tests for all marketability bands + empty input

## 4) One unresolved policy choice
`move_value` method must be formally locked (mean/median/weighted/trimmed).
Until this is pinned in product policy, different teams can ship different numbers while still claiming compliance.
