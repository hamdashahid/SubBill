# Architecture

```mermaid
flowchart TB
  CSV[Uploaded statement CSV] --> VALIDATE[Python validation and SHA-256]
  VALIDATE --> PARSE[Transaction parser / merchant normalization]
  PARSE --> DB[(SQLite authoritative memory)]
  DB --> GRAPH[LangGraph StateGraph]
  GRAPH --> LOAD[Load scoped register, evidence, decisions]
  LOAD --> ANALYZE[Deterministic recurrence analysis]
  ANALYZE --> LLM[Groq or offline mock recommendation]
  LLM --> POLICY[Python schema and evidence validation]
  POLICY --> UI[Streamlit findings and evidence]
  UI --> APPROVAL[Explicit human Keep / Cancel / Review Later]
  APPROVAL --> DB
  UI --> DRAFT[UNSENT cancellation draft]
  DRAFT --> DB
  DB --> EXPORT[One-way register snapshot]
```

## Trust boundaries

1. CSV values, descriptions and memo fields are untrusted data.
2. The LLM sees evidence as data and returns a bounded JSON recommendation.
3. Python validates action names and evidence references. Invalid results become escalation.
4. The user, not the model, approves subscription decisions.
5. No external action executor exists. Cancellation drafts are local text only.

## Components

- Streamlit: presentation and explicit approval controls.
- `subbill.tools`: parsing, normalization, detection, evidence, decisions, correction versioning and drafts.
- `subbill.graph`: LangGraph orchestration and memory retrieval.
- `subbill.llm`: Groq SDK adapter and deterministic mock.
- `subbill.db`: SQLite schema and per-user data access.
- `subbill.export`: read-only CSV/JSON snapshots.
