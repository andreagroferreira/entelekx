# EntelekX — Phase 5: Adaptive Context

## Goal

Make EntelekX learn the user and adapt to them.

## Deliverables

- [ ] User model structure:
  - Preferences.
  - Communication style.
  - Active goals.
  - Risk tolerance.
- [ ] Project model structure:
  - Stack, state, open questions.
  - Recent changes.
  - Risks.
- [ ] Memory extraction pipeline:
  - Explicit user-saved memories.
  - Proposed implicit memories.
- [ ] Context injection:
  - Compress and inject user/project model.
  - Retrieve relevant memories per prompt.
- [ ] Feedback loop:
  - Rating responses.
  - Correcting the agent.
  - Updating models.
- [ ] Weekly review agent:
  - Summarise progress.
  - Suggest next actions.
  - Update goals.

## Out of Scope

- Fully autonomous agent behaviour.
- Training custom models.

## Definition of Done

After a week of use, EntelekX proactively references the user's projects, preferences and past decisions without being asked.

## Related

- [[../10_Architecture/11_Adaptive_Context]]
- [[../10_Architecture/03_Data_Architecture]]
- [[../10_Architecture/05_Vector_Store_Abstraction]]
