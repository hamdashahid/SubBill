# Subbill

An offline-first subscription and bill review assistant for AI-4015. It
parses synthetic CSV statements, persists scoped SQLite memory, identifies
recurring-charge issues, and produces recommendations. It never performs
payments, cancellations, email, or network actions.

## Setup

Python 3.10+ is required. Create a virtual environment, run `pip install -r
requirements.txt`, generate data with `python data\generate_data.py`, then
follow [docs/demo_script.md](docs/demo_script.md). Run the web app locally with
`streamlit run app.py`. All commands support
`--llm mock`; real providers require a provider adapter and the user's own
API key in `.env`, never in source control.

## Deploy on Streamlit Community Cloud

1. Push this repository to GitHub.
2. Sign in at [share.streamlit.io](https://share.streamlit.io/) and choose
   **Create app**.
3. Select this repository and branch, and set the main file path to `app.py`.
4. Deploy. The app uses the `mock` provider by default and needs no secrets.
   To use Groq, add `GROQ_API_KEY` under the app's **Settings → Secrets**, then
   select `groq` in the app.

**Important:** this app has no login or access control, and Community Cloud's
local filesystem is not durable storage. The SQLite database can be reset when
the app restarts or redeploys, and users of a public app may access its shared
workspace. Use synthetic/demo data only; do not upload real statements or
other sensitive financial information. Persistent, private use requires
adding authentication and an external persistent database.

## Evaluation

Run `pytest`, `python -m subbill.run_scenarios`, `python -m subbill.ablation`,
and `python -m subbill.metrics`. Generated evidence belongs in `results/`.
The mock path is reproducible and is the path used by the automated tests.

The correction workflow is two-step: run `correct` without `--confirm` to
record a proposal, then repeat it with `--confirm` to supersede the current
register version. The scenario, ablation, and metrics modules also accept the
notebook options `--llm PROVIDER --out DIRECTORY`.
