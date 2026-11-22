# Subscription and Bill Assistant

This assistant helps a student review recurring personal charges without
accessing a bank, making payments, sending email, or cancelling anything.
CSV statements are parsed into SQLite; deterministic recurrence analysis finds
amount changes, duplicates, unknown merchants, and bills after cancellation.
A bounded mock/provider decision layer recommends an action, while the user
retains approval. SQLite is the long-term memory and every record is scoped by
user. A minimum demo ingests three cycles, adds evidence, records a gym
cancellation, restarts, and exports a one-way register view.
