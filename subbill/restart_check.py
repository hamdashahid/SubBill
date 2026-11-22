"""Cold-process restart proof using the supplied three statement cycles.

This check deliberately uses two independent Python processes and one SQLite file.
The child phases are invoked by this module's CLI; no chat or in-memory state is shared.
"""
from __future__ import annotations
import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from .db import connect, current_decision
from .tools import add_evidence, analyze_recurrence, decide, parse_statement_csv
from .export import export_register


def _phase_one(db_path: Path, data: Path, out: Path) -> dict:
    db = connect(db_path)
    cycle1 = parse_statement_csv(db, "hamda", data / "cycle1.csv", 1)
    cycle2 = parse_statement_csv(db, "hamda", data / "cycle2.csv", 2)
    add_evidence(db, "hamda", "netflix", "Used weekly; retain based on regular use.", "restart-check")
    decide(db, "hamda", "netflix", "keep", "Used weekly; keep subscription.")
    decide(db, "hamda", "gym", "cancel", "User requested cancellation.", "2026-02-06 12:00:00")
    export_register(db, "hamda", out / "before_restart")
    db.close()
    return {"cycle1_rows": cycle1, "cycle2_rows": cycle2, "database_closed": True}


def _phase_two(db_path: Path, data: Path, out: Path) -> dict:
    db = connect(db_path)
    cycle3 = parse_statement_csv(db, "hamda", data / "cycle3.csv", 3)
    findings = [dict(x) for x in analyze_recurrence(db, "hamda", 3)]
    decision = current_decision(db, "hamda", "netflix")
    evidence = [dict(x) for x in db.execute(
        "SELECT * FROM evidence WHERE user_id=? AND merchant_key=? ORDER BY id",
        ("hamda", "netflix"),
    )]
    result = {
        "cycle3_rows": cycle3,
        "retrieved_decision": dict(decision) if decision else None,
        "retrieved_evidence": evidence,
        "cycle3_findings": findings,
        "same_sqlite_file_reopened_in_new_process": True,
    }
    export_register(db, "hamda", out / "after_restart")
    db.close()
    result["passed"] = bool(
        cycle3 == 10
        and decision
        and decision["decision"] == "keep"
        and evidence
        and any(x["type"] == "DUPLICATE_CHARGE" and x["merchant_key"] == "netflix" for x in findings)
        and any(x["type"] == "CANCELLED_STILL_BILLED" and x["merchant_key"] == "gym" for x in findings)
    )
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="results/restart_check")
    args = parser.parse_args()
    root = Path(__file__).resolve().parent.parent
    data = root / "data" / "statements"
    out = Path(args.out).resolve()
    out.mkdir(parents=True, exist_ok=True)
    db_path = out / "restart_check.db"
    if db_path.exists():
        db_path.unlink()
    env = os.environ.copy()
    env["PYTHONPATH"] = str(root) + os.pathsep + env.get("PYTHONPATH", "")
    first_code = (
        "from pathlib import Path; from subbill.restart_check import _phase_one; "
        f"print(__import__('json').dumps(_phase_one(Path({str(db_path)!r}), Path({str(data)!r}), Path({str(out)!r}))))"
    )
    second_code = (
        "from pathlib import Path; from subbill.restart_check import _phase_two; "
        f"print(__import__('json').dumps(_phase_two(Path({str(db_path)!r}), Path({str(data)!r}), Path({str(out)!r}))))"
    )
    first = json.loads(subprocess.check_output([sys.executable, "-c", first_code], cwd=root, env=env, text=True))
    second = json.loads(subprocess.check_output([sys.executable, "-c", second_code], cwd=root, env=env, text=True))
    result = {"phase_one": first, "phase_two": second, "passed": bool(first["cycle1_rows"] == 9 and first["cycle2_rows"] == 9 and second["passed"])}
    (out / "restart_check.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))
    if not result["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
