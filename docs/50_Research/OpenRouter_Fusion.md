# OpenRouter Fusion

## Summary

OpenRouter Fusion is a **multi-model deliberation** feature. When invoked, it runs a panel of models in parallel, a judge compares their responses, and a final model uses the structured analysis to produce a better answer.

## Pipeline

1. User request → model.
2. Model invokes `openrouter:fusion`.
3. **Panel** (up to 8 models) answers in parallel with web tools.
4. **Judge** compares outputs and returns structured JSON.
5. **Final model** writes the answer using the analysis.

## Configuration

```json
{
  "model": "openrouter/fusion",
  "plugins": [
    {
      "id": "fusion",
      "analysis_models": ["~anthropic/claude-opus-latest", "~openai/gpt-latest"],
      "model": "~openai/gpt-latest"
    }
  ]
}
```

## Judge Output Schema

- `consensus`
- `contradictions`
- `partial_coverage`
- `unique_insights`
- `blind_spots`

## Key Properties

- Recursion protection: panel/judge cannot call Fusion again.
- Cost/latency trade-off configurable via presets.
- Useful for research, expert critique and complex decisions.

## EntelekX Implementation Notes

- Build our own Fusion engine, not a wrapper around OpenRouter's.
- Allow users to choose any models they have access to.
- Integrate with the Agent Kernel so Fusion is invoked automatically or on demand.
- Show cost and latency to the user.
- Bound recursion to depth 1.

## Related

- [[../10_Architecture/07_Fusion_Engine]]
- [[../20_Specs/SPEC-002_Fusion_Engine]]
