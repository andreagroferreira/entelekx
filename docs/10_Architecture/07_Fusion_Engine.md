# EntelekX — Fusion Engine

## Goal

Implement a native multi-model deliberation engine, inspired by OpenRouter Fusion, where EntelekX runs a panel of models in parallel, a judge compares their outputs, and the final response is synthesised from structured analysis.

## Pipeline

```
User request
    ↓
Planner decides if Fusion is needed
    ↓
Panel of models answers in parallel (each with web search if enabled)
    ↓
Judge model receives all panel outputs
    ↓
Judge produces structured analysis:
   - consensus
   - contradictions
   - partial_coverage
   - unique_insights
   - blind_spots
    ↓
Final model writes the answer using the analysis
```

## Configuration

```json
{
  "fusion": {
    "enabled": true,
    "mode": "auto",
    "analysis_models": [
      "openrouter/anthropic/claude-opus-latest",
      "openrouter/openai/gpt-latest",
      "openrouter/google/gemini-pro-latest"
    ],
    "judge_model": "openrouter/anthropic/claude-opus-latest",
    "final_model": "openrouter/anthropic/claude-sonnet-latest",
    "max_tool_calls": 8,
    "presets": {
      "general-high": { ... },
      "general-budget": { ... },
      "coding": { ... },
      "research": { ... }
    }
  }
}
```

## Modes

| Mode | Behaviour |
|---|---|
| `auto` | Agent decides when to invoke Fusion |
| `always` | Use Fusion for every request |
| `manual` | User toggles per request |
| `never` | Disable Fusion |

## Recursion Protection

- Inner Fusion calls carry a depth header.
- Panel and judge models cannot recursively invoke Fusion.
- Depth is bounded to 1.

## Cost and Latency Awareness

- Show estimated cost before running large panels.
- Track latency per model.
- Allow budget limits per request.

## Output Format

The judge returns a structured JSON object. The final model receives it in a system message.

```json
{
  "consensus": ["point A", "point B"],
  "contradictions": [{"claim": "...", "models": ["a", "b"]}],
  "partial_coverage": ["..."],
  "unique_insights": {"model_a": "...", "model_b": "..."},
  "blind_spots": ["..."]
}
```

## Related

- [[06_Agent_Runtime]]
- [[02_Technical_Stack]]
- [[50_Research/OpenRouter_Fusion]]
- [[20_Specs/SPEC-002_Fusion_Engine]]
