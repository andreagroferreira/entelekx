# EntelekX — Adaptive Context

## Goal

EntelekX should know the user better over time. Every interaction should make the system more useful, personalised and predictive — without being creepy.

## What We Learn

| Dimension | Examples |
|---|---|
| **Preferences** | Communication style, risk tolerance, tool choices, model preferences |
| **Projects** | Active projects, their goals, their tech stacks, their state |
| **Decisions** | Past choices and outcomes |
| **Habits** | Working hours, recurring workflows, common requests |
| **Knowledge** | Domain expertise, definitions, mental models |
| **Communication style** | Tone, length, language, emoji usage |
| **Failures** | What approaches did not work |

## Mechanisms

### 1. Explicit Memory

User can save facts, preferences and rules via chat or UI. Stored as `Memory` entities with embeddings.

### 2. Implicit Extraction

After conversations, the agent extracts:
- New facts about the user.
- New project state.
- Decisions made.
- Preferences inferred.

Extracted items are proposed to the user for confirmation before storage.

### 3. User Model

A structured representation (JSON/Pydantic) that summarises the user's profile, goals, active projects and preferences. It is injected into prompts in a compressed form.

### 4. Project Model

A structured representation per project: goals, stack, open questions, recent changes, risks.

### 5. Context Injection

Every prompt is enriched with:
- A compressed user model.
- Relevant memories (vector search + keyword).
- Relevant project state.
- Recent decisions and tasks.

### 6. Feedback Loop

User can rate responses and correct the agent. Corrections update the user/project model and memory.

## Privacy

- All learning happens locally.
- User controls what is stored.
- Option to review and delete memories.
- No telemetry of personal data.

## Related

- [[06_Agent_Runtime]]
- [[09_Life_OS]]
- [[03_Data_Architecture]]
- [[05_Vector_Store_Abstraction]]
