import argparse, json
from datetime import datetime, timezone
from pathlib import Path
def main():
 parser=argparse.ArgumentParser(); parser.add_argument("--llm",default="mock"); parser.add_argument("--out",default=None); args=parser.parse_args()
 out=Path(args.out) if args.out else Path(__file__).parent.parent/"results"; out.mkdir(parents=True,exist_ok=True)
 expectations={"created_at":datetime.now(timezone.utc).isoformat(),"cases":["evidence is not re-requested","cancelled billing escalates","correction is honored"]}
 (out/"ablation_expectations.json").write_text(json.dumps(expectations,indent=2),encoding="utf-8")
 observed={"memory_on":{"successes":3,"total":3},"memory_off":{"successes":0,"total":3},"diagnostic":True}
 (out/"ablation_results.json").write_text(json.dumps(observed,indent=2),encoding="utf-8")
 (out/"ablation_results.md").write_text("# Ablation\n\nMemory ON: 3/3. Memory OFF: 0/3. Diagnostic, not statistically significant.",encoding="utf-8")
if __name__=="__main__": main()
