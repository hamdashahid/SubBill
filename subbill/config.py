from pathlib import Path
import os

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DB = ROOT / "subbill.db"
RESULTS = ROOT / "results"
MODEL = os.getenv("LLM_MODEL", "mock-v1")

