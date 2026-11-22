# Memory lifecycle

Transactions and source-file hashes are written at ingestion. The current
register, decisions, evidence, issues, drafts, and action log are retrieved
only for the requested `user_id`. Decisions are versioned by superseding old
rows; drafts and ingestion use idempotency hashes. Exports never write back to
the database. CSV and evidence text is treated as untrusted data and cannot
add tools or recipients.
