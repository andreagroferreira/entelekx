---
type: spec
status: draft
feature: life-os
project: entelekx
date_created: 2026-06-21
tags: [spec, entelekx, productivity, knowledge]
---

# SPEC-004: Life OS

## Overview

**Problem:** Founders and solo builders manage their life and business across Notion, ClickUp, Google Calendar, notes apps and chat tools. Context is fragmented. Decisions are forgotten. Goals drift.

**Goal:** Implement the Life OS: notes, tasks, calendar, goals, decisions and a knowledge graph — all unified with the agent and project context.

**Actors:**
- User (manages life/business).
- Agent Kernel (extracts tasks, decisions and insights).
- Life OS modules (notes, tasks, calendar, goals, decisions).
- Knowledge graph engine.

## Scope

### In scope

- Notes with Markdown, backlinks and graph.
- Tasks with projects, priorities, due dates and recurrence.
- Calendar view with scheduled agent tasks and reminders.
- Goals with hierarchy and progress.
- Decision log with reasoning and outcome.
- Knowledge graph extraction and exploration.
- AI-assisted extraction from conversations.

### Out of scope

- External calendar sync (CalDAV) in MVP.
- Email integration in MVP.
- Mobile companion in MVP.
- Complex project management (Gantt, resource allocation).

## Acceptance Criteria

1. **Given** a user in chat, **when** they say "create a task to follow up with Maria", **then** a task is created and linked to the current project.
2. **Given** a note, **when** the user mentions another note, **then** a backlink is created and visible.
3. **Given** a goal, **when** tasks are completed under it, **then** progress is updated.
4. **Given** a conversation, **when** a decision is made, **then** the agent proposes logging it.
5. **Given** the knowledge graph, **when** the user explores a node, **then** related entities are shown.
6. **Given** a weekly review request, **when** the agent runs, **then** it summarises tasks, decisions and open goals.

## Data Model

### `notes`

| Field | Type | Description |
|---|---|---|
| id | uuid | PK |
| project_id | uuid | FK |
| title | str | |
| body | text | Markdown |
| tags | jsonb | List of tags |
| backlinks | jsonb | IDs of linked notes |
| created_at | datetime | |
| updated_at | datetime | |

### `tasks`

| Field | Type | Description |
|---|---|---|
| id | uuid | PK |
| project_id | uuid | FK |
| goal_id | uuid | FK optional |
| title | str | |
| status | enum | `todo`, `in_progress`, `done`, `cancelled` |
| priority | enum | `low`, `medium`, `high` |
| due_date | datetime | Optional |
| recurrence | str | Optional (RRULE-like) |
| delegated_to | str | Optional agent/skill |
| created_at | datetime | |
| updated_at | datetime | |

### `goals`

| Field | Type | Description |
|---|---|---|
| id | uuid | PK |
| project_id | uuid | FK |
| parent_id | uuid | FK optional |
| title | str | |
| status | enum | `active`, `completed`, `paused` |
| progress | int | 0-100 |
| target_date | datetime | Optional |

### `decisions`

| Field | Type | Description |
|---|---|---|
| id | uuid | PK |
| project_id | uuid | FK |
| question | str | |
| options | jsonb | Options considered |
| reasoning | text | |
| decision | text | Chosen option |
| outcome | text | Optional follow-up |
| created_at | datetime | |

### `events`

| Field | Type | Description |
|---|---|---|
| id | uuid | PK |
| project_id | uuid | FK |
| title | str | |
| start_time | datetime | |
| end_time | datetime | Optional |
| recurrence | str | Optional |
| source | enum | `user`, `agent`, `calendar_sync` |

### `knowledge_graph_entities`

| Field | Type | Description |
|---|---|---|
| id | uuid | PK |
| project_id | uuid | FK |
| name | str | |
| type | enum | `person`, `company`, `concept`, `product`, `idea` |
| summary | text | |
| source_ids | jsonb | IDs of notes/messages |

### `knowledge_graph_relations`

| Field | Type | Description |
|---|---|---|
| id | uuid | PK |
| source_id | uuid | FK entity |
| target_id | uuid | FK entity |
| relation | str | e.g. `works_at`, `related_to`, `part_of` |

## API Contracts

### Notes

- `GET /api/v1/notes`
- `POST /api/v1/notes`
- `GET /api/v1/notes/{id}`
- `PUT /api/v1/notes/{id}`
- `DELETE /api/v1/notes/{id}`
- `GET /api/v1/notes/graph` — graph data.

### Tasks

- `GET /api/v1/tasks`
- `POST /api/v1/tasks`
- `PUT /api/v1/tasks/{id}`
- `DELETE /api/v1/tasks/{id}`

### Goals

- `GET /api/v1/goals`
- `POST /api/v1/goals`
- `PUT /api/v1/goals/{id}`
- `DELETE /api/v1/goals/{id}`

### Decisions

- `GET /api/v1/decisions`
- `POST /api/v1/decisions`
- `PUT /api/v1/decisions/{id}`

### Calendar

- `GET /api/v1/events`
- `POST /api/v1/events`
- `PUT /api/v1/events/{id}`
- `DELETE /api/v1/events/{id}`

### Knowledge Graph

- `GET /api/v1/knowledge-graph`
- `GET /api/v1/knowledge-graph/entities/{id}`

## UI/UX Requirements

### Dashboard

- Today's focus: top tasks, upcoming events, active goal progress.
- Quick capture: "Add note / task / decision".

### Notes

- Split editor/preview or WYSIWYG.
- Backlink autocomplete.
- Graph view toggle.
- AI buttons: summarise, extract tasks, find related.

### Tasks

- Board view (Kanban) and list view.
- Filters: project, status, priority, due date.
- Recurring task indicator.
- Create from chat.

### Calendar

- Month/week/day views.
- Drag to reschedule.
- Agent-scheduled events colour-coded.

### Goals

- Tree view.
- Progress bars.
- Link tasks.

### Decisions

- Timeline feed.
- Outcome field editable for retrospectives.

### Knowledge Graph

- Force-directed graph.
- Click entity to see summary and relations.
- Add/edit entities manually.

## Edge Cases

1. **Circular backlinks:** detect and prevent infinite loops.
2. **Recurrence forever:** store recurrence rule, expand on demand.
3. **Goal deletion with child tasks:** prompt to reassign or archive.
4. **Duplicate entity names:** merge suggestions.
5. **AI extracts false memory:** user can reject.
6. **Large knowledge graph:** lazy load and cluster.

## Test Scenarios

| # | Scenario | Type | Expected |
|---|---|---|---|
| 1 | Create note from chat | Integration | Note created with project link |
| 2 | Backlink creates graph edge | Integration | Linked notes appear in graph |
| 3 | Complete task updates goal progress | Integration | Progress recalculated |
| 4 | Agent proposes decision log | E2E | Decision draft shown for approval |
| 5 | Knowledge graph shows related entities | Integration | Graph data returned |
| 6 | Weekly review summary | Integration | Covers tasks, goals, decisions |
| 7 | Recurring task generates next instance | Unit | Next due date calculated |

## Dependencies

- [ ] SPEC-001 Agent Kernel.
- [ ] SPEC-006 Database Abstraction.
- [ ] SPEC-007 Vector Store Abstraction.
- [ ] Markdown parser and backlink extractor.

## Open Questions

- Should notes be Obsidian-compatible for portability?
- Should tasks use a specific recurrence format (iCal RRULE)?
- How aggressively should the agent extract entities automatically?

## Related

- [[10_Architecture/09_Life_OS]]
- [[40_Roadmap/Phase_4_Life_OS]]
