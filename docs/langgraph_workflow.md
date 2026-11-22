# LangGraph workflow

```mermaid
flowchart TD
  START([START]) --> PARSE[Parse statement and analyze deterministic billing evidence]
  PARSE --> MEMORY[Load persistent register, prior decisions and usage evidence]
  MEMORY --> DECIDE[LLM decision using retrieved evidence]
  DECIDE --> VALIDATE[Validate action and evidence references]
  VALIDATE --> ROUTE{Any findings need approval?}
  ROUTE -->|Yes| WAIT[Return findings with approval required]
  ROUTE -->|No| END([END])
  WAIT --> END2([END: frontend waits for user])
  END2 --> HUMAN[Human chooses Keep / Cancel / Review Later]
  HUMAN --> RECORD[Record decision in SQLite]
  RECORD --> DRAFT[Optional UNSENT cancellation draft]
```

The currently implemented compiled graph uses LangGraph `StateGraph` with `START`, four named nodes (`parse_statement`, `load_persistent_memory`, `analyze_and_decide`, `awaiting_human_approval`), explicit edges, a conditional route based on whether findings need approval, and `END`. The user approval step is intentionally outside the graph so the model cannot approve itself or execute a cancellation. The frontend writes the user's decision to SQLite after explicit interaction. `review()` raises a clear dependency error if LangGraph is not installed; it does not silently substitute a fake graph.
