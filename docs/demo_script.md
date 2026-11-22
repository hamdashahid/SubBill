# Demo script

```powershell
python data\generate_data.py
python -m subbill.cli --db demo.db init
python -m subbill.cli --db demo.db ingest --file data\statements\cycle1.csv --cycle 1
python -m subbill.cli --db demo.db review --cycle 1
python -m subbill.cli --db demo.db ingest --file data\statements\cycle2.csv --cycle 2
python -m subbill.cli --db demo.db review --cycle 2
python -m subbill.cli --db demo.db decide --merchant gym --decision cancel --reason "not used"
python -m subbill.cli --db demo.db draft-cancellation --merchant gym
python -m subbill.cli --db demo.db state
python -m subbill.cli --db demo.db ingest --file data\statements\cycle3.csv --cycle 3
python -m subbill.cli --db demo.db review --cycle 3
python -m subbill.cli --db demo.db correct --merchant netflix --field renewal_date --value 2026-11-05 --reason "Provider confirmed new date"
python -m subbill.cli --db demo.db correct --merchant netflix --field renewal_date --value 2026-11-05 --reason "Provider confirmed new date" --confirm
python -m subbill.cli --db demo.db review --cycle 3
python -m subbill.cli --db demo.db export --out-dir results
```

Run each command as a separate process to demonstrate restart-safe SQLite
memory. Use `--llm mock` explicitly for offline CI.
