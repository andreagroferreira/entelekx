# Open Design Analysis

## Summary

`nexu-io/open-design` is an open-source, agent-native design platform. It generates real UI artefacts (HTML, React, Next.js, Vue, decks, images, video) using agent CLIs already installed on the user's machine.

## Key Takeaways

- **Artefact-first, not canvas-first.** The agent writes real code, previewed in a sandboxed iframe.
- **DESIGN.md as brand contract.** 150+ design systems define visual rules injected into prompts.
- **Skills + plugins ecosystem.** 259 skills, 261 plugins, export tools for React/Next/Vue.
- **MCP server.** Allows other agents to read/write Open Design projects.
- **Integrates with 22+ agents** including Claude Code, Codex, Cursor, Hermes, OpenClaw.

## Relevance to EntelekX

Open Design is the ideal **creative/frontend layer** for EntelekX. It proves that:
- Design can be agent-driven and code-first.
- `DESIGN.md` is a useful standard for brand consistency.
- Generated artefacts can be handed off to a dev agent.

## How EntelekX Differs

- EntelekX integrates design generation **inside** the same workspace as coding, decisions and memory.
- EntelekX generates **full-stack applications**, not just UI artefacts.
- EntelekX has native **Fusion** and **adaptive context**.

## Strategic Recommendation

Adopt the `DESIGN.md` pattern and Open Design-inspired artefact generation, but build the integration as a **module** inside EntelekX, not as a separate tool. Expose generated designs to the Dev Studio for full-stack implementation.

## Related

- [[../10_Architecture/08_Dev_Studio]]
- [[../10_Architecture/10_Media_Forge]]
- [[../40_Roadmap/Phase_3_Dev_Studio]]
- [[../40_Roadmap/Phase_6_Media_Omnichannel]]
