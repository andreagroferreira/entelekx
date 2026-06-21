---
type: spec
status: draft
feature: fusion-engine
project: entelekx
date_created: 2026-06-21
tags: [spec, entelekx, fusion, multi-model, ai]
---

# SPEC-002: Fusion Engine

## Overview

**Problem:** A single model can be wrong, biased or narrow. Complex research, strategic or expert tasks benefit from multiple perspectives. Existing tools either compare models side-by-side or require manual orchestration.

**Goal:** Implement a native multi-model deliberation engine where EntelekX runs a panel of models in parallel, a judge synthesises their outputs and a final model produces a grounded answer.

**Actors:**
- User (requests analysis).
- Agent Kernel (decides when to invoke Fusion).
- Fusion Engine (orchestrates panel and judge).
- Provider adapters (for panel and judge models).
- Final answer model.

## Scope

### In scope

- Fusion configuration (presets, custom panels).
- Panel execution in parallel.
- Judge model with structured JSON output.
- Final answer synthesis.
- Recursion protection.
- Cost/latency tracking and budget limits.
- UI toggle and progress.

### Out of scope

- OpenRouter Fusion API direct wrapper (we build our own).
- Automatic panel model selection beyond presets in MVP.
- Recursive deliberation beyond one level.

## Acceptance Criteria

1. **Given** a complex user prompt, **when** Fusion is invoked, **then** the panel models run in parallel.
2. **Given** panel outputs, **when** the judge runs, **then** it returns structured analysis with consensus, contradictions, blind spots and unique insights.
3. **Given** the judge analysis, **when** the final model runs, **then** it writes an answer grounded in the analysis.
4. **Given** auto-mode, **when** the prompt is simple, **then** Fusion is skipped and the model answers directly.
5. **Given** Fusion depth already 1, **when** a panel/judge model tries to call Fusion, **then** the tool is not injected.
6. **Given** a cost cap, **when** the panel exceeds it, **then** the run aborts with a clear message.
7. **Given** the UI, **when** Fusion runs, **then** the user sees progress and can view the judge analysis.

## Data Model

### `fusion_runs` table

| Field | Type | Description |
|---|---|---|
| id | uuid | PK |
| session_id | uuid | FK |
| user_message_id | uuid | FK |
| preset | str | Preset slug or `custom` |
| analysis_models | jsonb | List of model slugs |
| judge_model | str | Judge model slug |
| final_model | str | Final model slug |
| status | enum | `running`, `completed`, `failed`, `aborted` |
| cost_usd | float | Estimated actual cost |
| latency_ms | int | Total elapsed time |
| judge_analysis | jsonb | Structured analysis |
| created_at | datetime | |
| completed_at | datetime | |

### `fusion_panel_outputs` table

| Field | Type | Description |
|---|---|---|
| id | uuid | PK |
| fusion_run_id | uuid | FK |
| model | str | Panel model slug |
| content | text | Panel response |
| tool_calls_used | int | How many tool calls |
| latency_ms | int | |
| cost_usd | float | |

## API Contracts

### Internal

```python
class FusionEngine:
    async def run(
        self,
        request: FusionRequest,
        context: list[AgentMessage],
    ) -> FusionResult: ...
```

### HTTP

- `POST /api/v1/sessions/{id}/fusion` — manually trigger Fusion.
- `GET /api/v1/sessions/{id}/fusion/{run_id}` — get run details.

### Judge Analysis Schema

```json
{
  "consensus": ["string"],
  "contradictions": [
    {
      "claim": "string",
      "supporting_models": ["string"],
      "opposing_models": ["string"]
    }
  ],
  "partial_coverage": ["string"],
  "unique_insights": {
    "model_slug": "string"
  },
  "blind_spots": ["string"],
  "confidence": "high" | "medium" | "low"
}
```

## UI/UX Requirements

### Chat toolbar

- "Use Fusion" toggle (auto / always / never).
- Hover tooltip explaining what Fusion does.

### Fusion progress

- Panel progress indicator: "3 of 3 models complete".
- Judge step indicator.
- Final answer streaming.

### Analysis view

- Collapsible card showing judge analysis.
- Highlight consensus, contradictions and blind spots.
- Show cost and latency.

## Configuration

```json
{
  "fusion": {
    "mode": "auto",
    "presets": {
      "general-high": {
        "analysis_models": [
          "openrouter/anthropic/claude-opus-latest",
          "openrouter/openai/gpt-latest",
          "openrouter/google/gemini-pro-latest"
        ],
        "judge_model": "openrouter/anthropic/claude-opus-latest",
        "final_model": "openrouter/anthropic/claude-sonnet-latest",
        "max_tool_calls": 8,
        "cost_limit_usd": 2.0
      },
      "general-budget": { ... },
      "coding": { ... },
      "research": { ... }
    }
  }
}
```

## Edge Cases

1. **Panel model fails:** use partial output or mark as unavailable; continue.
2. **Judge returns invalid JSON:** retry once, then fall back to plain summary.
3. **All panel models disagree:** judge reports high contradiction, final answer is cautious.
4. **Cost limit exceeded mid-panel:** abort and inform user.
5. **Latency too high:** allow user to cancel and get a direct answer.
6. **Tool call in panel loops too long:** enforce `max_tool_calls`.

## Test Scenarios

| # | Scenario | Type | Expected |
|---|---|---|---|
| 1 | Auto-mode skips Fusion for simple prompt | Unit | Direct answer |
| 2 | Panel runs 3 models in parallel | Integration | All outputs collected |
| 3 | Judge produces valid JSON | Integration | Analysis returned |
| 4 | Final answer uses analysis | Integration | Grounded response |
| 5 | Recursion protection blocks nested Fusion | Unit | Tool not injected |
| 6 | Cost cap aborts run | Integration | Error returned |
| 7 | Panel model failure handled | Integration | Run continues with remaining models |
| 8 | UI shows progress and analysis | E2E | User sees all stages |

## Dependencies

- [ ] SPEC-001 Agent Kernel.
- [ ] Provider adapters support parallel requests.
- [ ] Structured output support (JSON mode or tools) for judge.
- [ ] Cost tracking per model.

## Open Questions

- Should the same model act as judge and final answer writer?
- Should panel models have access to web tools by default?
- How do we expose "when to use Fusion" guidance to users?

## Related

- [[SPEC-001_Agent_Kernel]]
- [[10_Architecture/07_Fusion_Engine]]
- [[50_Research/OpenRouter_Fusion]]
