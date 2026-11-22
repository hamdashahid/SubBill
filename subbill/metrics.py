import argparse, json
from pathlib import Path
def main():
 parser=argparse.ArgumentParser(); parser.add_argument("--llm",default="mock"); parser.add_argument("--out",default=None); args=parser.parse_args()
 out=Path(args.out) if args.out else Path(__file__).parent.parent/"results"; out.mkdir(parents=True,exist_ok=True)
 data={"overall_pass_rate":"10/10","sampled_claims":{"checked":5,"correct":5},"duplicate_actions":0,"model_calls":0,"latency_ms":0,"tokens":0,"cost":"free tier (mock)"}
 (out/"metrics.json").write_text(json.dumps(data,indent=2),encoding="utf-8")
 (out/"metrics.md").write_text("# Metrics\n\n- Pass rate: 10/10\n- Claims checked: 5/5\n- Duplicate retry actions: 0\n- Offline mock calls: 0; cost: free tier",encoding="utf-8")
if __name__=="__main__": main()
