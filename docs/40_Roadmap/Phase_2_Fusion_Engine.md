# EntelekX — Phase 2: Fusion Engine

## Goal

Implement native multi-model deliberation.

## Deliverables

- [ ] Fusion configuration model and UI.
- [ ] Presets: `general-high`, `general-budget`, `coding`, `research`.
- [ ] Panel execution in parallel.
- [ ] Judge model with structured JSON output.
- [ ] Final answer synthesis.
- [ ] Recursion protection.
- [ ] Cost and latency tracking.
- [ ] UI: toggle Fusion, panel progress, judge analysis view.
- [ ] Tests for each preset and edge case.

## Out of Scope

- External OpenRouter Fusion API (we build our own).
- Automatic panel model selection beyond presets.

## Definition of Done

A user can enable Fusion for a complex prompt, see multiple models respond, read the judge's analysis and receive a final synthesised answer.

## Related

- [[../20_Specs/SPEC-002_Fusion_Engine]]
- [[../10_Architecture/07_Fusion_Engine]]
- [[../50_Research/OpenRouter_Fusion]]
