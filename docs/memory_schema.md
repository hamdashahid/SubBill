# SQLite memory schema

| Table | Purpose | Versioning / isolation |
|---|---|---|
| `transactions` | Every imported charge, source hash, cycle, row reference, currency and memo | Unique `(user_id, file_sha256, row_ref)` |
| `source_files` | Imported file hashes and metadata | Primary key `(user_id, sha256)` |
| `register_items` | Subscription amount, interval, next renewal, status and source | Per-user merchant versions; superseded rows retained |
| `decisions` | Keep/cancel/review-later decision, reason and timestamp | Current row supersedes prior decision; user scoped |
| `evidence` | Usage notes and source references | Append-only user/merchant records |
| `issues` | Detected duplicate/amount/cancelled billing anomalies | Unique idempotency key; open/resolved status |
| `corrections` | Proposed and approved register corrections | Append-only, confirmation flag |
| `drafts` | Local cancellation request text | Idempotent key; label `UNSENT` |
| `action_log` | Tool, timestamp, outcome, error, timing and memory read/write notes | Append-only, user scoped |

SQLite is the authoritative persistent memory. The app reopens the same database path after a process restart; no chat history or in-memory session is required to recover decisions. Database WAL mode is enabled. Additive migration adds the transaction currency field to the original assignment schema when needed.
