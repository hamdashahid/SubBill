# Subscription & Bill Assistant

An offline-first Agentic AI assistant for reviewing personal
subscriptions and recurring bills. The project analyzes statement CSVs,
identifies recurring charges and billing anomalies, retrieves decisions
from persistent local memory, and helps users decide whether to keep,
cancel, or review a subscription.

> **Project status:** Work in progress. This repository contains the
> initial Python/SQLite implementation and synthetic three-cycle
> datasets. The full LangGraph workflow, interactive Streamlit frontend,
> and complete evidence-backed evaluation are planned completion items.
> Do not treat planned capabilities as implemented until their tests and
> demo evidence are present.

## Project at a glance

  -----------------------------------------------------------------------
  Field                               Details
  ----------------------------------- -----------------------------------
  Project                             Subscription and Bill Assistant

  Assignment                          Practical Agentic Systems with
                                      Persistent Memory

  Project option                      D03 -- Subscription and bill
                                      assistant

  Student ID                          23i-0069

  Student                             Hamda Shahid

  Core language                       Python

  Current persistence                 SQLite

  Input                               Local statement CSV files

  LLM integration                     Provider adapter scaffold; mock
                                      mode for reproducible runs

  Planned agent orchestration         LangGraph

  Planned user interface              Streamlit
  -----------------------------------------------------------------------

## The problem

Individuals often manage subscriptions across multiple services and may
overlook recurring charges, duplicate billing, price increases,
renewal-date changes, or charges that continue after they have decided
to cancel. Reviewing each statement manually is repetitive, and
decisions made in one billing cycle should inform the next review.

The Subscription & Bill Assistant is designed to make this review
process repeatable while keeping the user in control.

## Intended workflow

1.  **Upload a statement:** provide a local CSV statement for a billing
    cycle.
2.  **Parse and validate:** read the transactions and validate the
    expected fields.
3.  **Analyze recurrence:** identify likely recurring merchants and
    compare transactions with the stored register.
4.  **Retrieve memory:** load relevant subscription details, usage
    evidence, prior decisions, and unresolved issues from SQLite.
5.  **Review anomalies:** surface possible duplicate charges, amount
    changes, renewal-date changes, and charges against previously
    cancelled items.
6.  **Recommend the next action:** present evidence and a recommendation
    to keep, cancel, or review later.
7.  **Request approval:** the user makes the decision; the system
    records the decision and reason.
8.  **Prepare a cancellation draft:** for a user-approved cancellation
    decision, generate text only and label it **UNSENT**.
9.  **Persist and log:** update the local register with history and
    record relevant tool calls, memory operations, and outcomes.
10. **Continue after restart:** a later process retrieves the saved
    state without requiring the original statement or chat history
    again.

The actual implemented workflow and supported commands are documented in
the source and demo instructions. The intended LangGraph and Streamlit
components will be marked complete only after they are implemented and
verified.

## Safety and approval boundaries

-   No bank-account connection or bank integrations.
-   No automatic payments.
-   No automatic subscription cancellations.
-   No emails are sent.
-   Cancellation requests are generated as **draft text only**.
-   User decisions and approved corrections must be explicit.
-   Deterministic code is responsible for validation, calculations,
    permissions, deduplication, and stable database updates.
-   CSV content is treated as untrusted data and must not be allowed to
    change application permissions or approval rules.
-   API keys and credentials must be stored outside source code and must
    never be committed.

## Repository structure

``` text
.
├── data/
│   ├── statements/           # Synthetic billing-cycle CSVs
│   ├── generate_data.py      # Synthetic data generator
│   └── README.md
├── docs/
│   ├── ai_disclosure.md
│   ├── demo_script.md
│   ├── memory_lifecycle.md
│   ├── proposal.md
│   └── report.md
├── results/                  # Generated evaluation and demo evidence
├── subbill/
│   ├── ablation.py
│   ├── cli.py
│   ├── config.py
│   ├── db.py
│   ├── export.py
│   ├── graph.py
│   ├── llm.py
│   ├── logger.py
│   ├── metrics.py
│   ├── policy.py
│   ├── run_scenarios.py
│   └── tools.py
├── tests/
│   └── test_core.py
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

Generated databases, local environment files, caches, and secrets should
not be committed. Keep synthetic sample data and reproducible,
non-sensitive evidence in the repository.

## Getting started

### Requirements

-   Python 3.10 or newer
-   Git
-   Windows, macOS, or Linux

### 1. Clone the repository

``` bash
git clone https://github.com/<your-username>/subscription-bill-assistant.git
cd subscription-bill-assistant
```

### 2. Create and activate a virtual environment

**Windows PowerShell**

``` powershell
py -3.10 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**macOS / Linux**

``` bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

``` bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure environment variables

Copy `.env.example` to `.env` and add only the configuration required by
the provider adapter you use. Keep `.env` out of Git.

``` powershell
Copy-Item .env.example .env
```

### 5. Generate the synthetic sample data

``` bash
python data/generate_data.py
```

### 6. Run the existing checks and demo workflow

``` bash
pytest
python -m subbill.run_scenarios
python -m subbill.ablation
python -m subbill.metrics
```

For the current CLI workflow and supported options, consult
`docs/demo_script.md` and the command-line help. The mock LLM mode is
intended for deterministic, reproducible local testing. Do not assume a
live provider is configured merely because a mock run succeeds.

## Persistent memory

SQLite is the local persistence layer. It is intended to retain
structured subscription state and decision history across separate
application processes. This is distinct from conversation history: the
restart demonstration must terminate the process and then retrieve the
required state from the database.

The memory lifecycle documentation is in
[`docs/memory_lifecycle.md`](docs/memory_lifecycle.md). The database
should remain the authoritative store; CSV/JSON exports are review
artifacts, not a replacement for the database.

## Three-cycle demonstration

The supplied synthetic data is designed for a three-cycle demonstration.

-   **Session 1:** process Cycles 1 and 2, collect usage evidence, and
    record user decisions.
-   **Restart:** stop the process completely and preserve the database
    on disk.
-   **Session 2:** start a fresh process, process Cycle 3, and verify
    that prior decisions and unresolved issues are retrieved from
    persistent storage.

The before-restart and after-restart register exports should be retained
as evidence. The demo must show actual retrieved records, not rely on
chat history or hardcoded output.

## Evaluation

The assignment requires at least ten distinct scenarios, including
initial use, later use, restart continuity, approved correction,
isolation, conflicting evidence, failure and retry, untrusted input,
duplicate billing, and cancelled-item rebilling.

Evaluation results must be generated by executing the scenarios. Do not
manually label unexecuted scenarios as passed or publish hardcoded
metrics. Clearly identify mock-mode results versus live-LLM results, and
record failures as well as successes.

See [`results/`](results/) and the evaluation scripts for generated
evidence. Results should be regenerated after implementation changes.

## Technology

-   **Python** --- application logic and analysis tools
-   **pandas** --- CSV transaction processing (where used by the
    implementation)
-   **SQLite** --- structured persistent local memory
-   **LLM provider adapter** --- language-model-assisted
    recommendations, with mock mode for repeatable tests
-   **LangGraph** --- planned explicit agent workflow orchestration
-   **Streamlit** --- planned interactive application interface
-   **pytest** --- automated testing

The exact installed and tested dependency versions should be maintained
in `requirements.txt` and reported in the technical documentation.

## Limitations

This is an educational prototype using synthetic statement data. It is
not a banking product, financial adviser, payment processor, or
subscription-management integration. Transaction classification can be
uncertain; users must inspect supporting evidence before making
decisions. No real cancellation or payment action is performed.

## Academic integrity and AI assistance

This is an individual assignment. External code, datasets, libraries,
and AI assistance must be disclosed in accordance with the course
instructions. See [`docs/ai_disclosure.md`](docs/ai_disclosure.md). The
student should understand, test, and be able to explain every submitted
component.

## License

No license has been selected yet. Unless a license is added, the
repository should be treated as all rights reserved by default.
