# Evaluation summary

This summary describes the checked-in run artifacts. Detailed observations, runtime versions and outputs are in `results/`.

| Test / scenario | Execution status | Evidence |
|---|---|---|
| Unit tests | 16 passed | `results/test_results.txt` |
| Initial use | PASS | `results/scenario_table.csv` |
| Later use | PASS | `results/scenario_table.csv` |
| Full process restart | PASS | `results/restart_check/restart_check.json`: process A ingested Cycles 1–2 and saved Netflix evidence/decision plus Gym cancellation; process B reopened the same SQLite file, ingested Cycle 3, and retrieved the saved Netflix decision/evidence |
| Approved correction | PASS | New register version recorded |
| User isolation | PASS | `user_b_cycle1.csv` ingested as `alex`; Hamda register unchanged |
| Missing/conflicting evidence | PASS | Unsupported evidence reference escalated by validator |
| Tool failure and retry | PASS | Injected transient exception, then retry |
| Untrusted instruction in CSV | PASS | Supplied instruction-like memo detected as untrusted |
| Duplicate billing | PASS | Cycle 3 duplicate retained and flagged |
| Cancelled subscription billed again | PASS | Explicit historical cancellation date precedes later charge |
| Month-end renewal projection | PASS | Added tests for Jan 31 → Feb 28, leap-year February, March 31 → April 30, and no false month-end shift |

## Three paired memory ablation cases

`results/ablation_results.json` records six actual mock calls: three identical issue inputs each evaluated with memory context on and off. Memory-on recommendations differ from memory-off recommendations in all three cases. This is a deterministic functional comparison, not a statistical performance study.

## Runtime boundary

The available runner executed Python 3.13.5, pytest 9.0.2, pandas 2.2.3, and python-dotenv 1.2.2. Python 3.11 is not installed here. LangGraph, Streamlit, and Groq were not installed. A pip dry-run of `requirements.txt` failed because DNS could not resolve the package index, so dependency pins and compatibility have not been independently confirmed in Python 3.11. Thus core tests and deterministic scenario/ablation runs are verified; LangGraph compilation, Streamlit launch, and live Groq calls are not verified. No live-model cost or token usage is claimed.
