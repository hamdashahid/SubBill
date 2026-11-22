# Subbill

An offline-first subscription and bill review assistant for AI-4015. It
parses synthetic CSV statements, persists scoped SQLite memory, identifies
recurring-charge issues, and produces recommendations. It never performs
payments, cancellations, email, or network actions.

## Setup

Python 3.10+ is required. Create a virtual environment, run `pip install -r
requirements.txt`, generate data with `python data\generate_data.py`, then
follow [docs/demo_script.md](docs/demo_script.md). All commands support
`--llm mock`; real providers require a provider adapter and the user's own
API key in `.env`, never in source control.

## Evaluation

Run `pytest`, `python -m subbill.run_scenarios`, `python -m subbill.ablation`,
and `python -m subbill.metrics`. Generated evidence belongs in `results/`.
The mock path is reproducible and is the path used by the automated tests.

The correction workflow is two-step: run `correct` without `--confirm` to
record a proposal, then repeat it with `--confirm` to supersede the current
register version. The scenario, ablation, and metrics modules also accept the
notebook options `--llm PROVIDER --out DIRECTORY`.
