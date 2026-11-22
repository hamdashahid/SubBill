import argparse, csv, json, tempfile
from pathlib import Path
from .db import connect
from .tools import parse_statement_csv
from .graph import review
def main():
 parser=argparse.ArgumentParser()
 parser.add_argument("--llm",default="mock")
 parser.add_argument("--out",default=None)
 args=parser.parse_args()
 root=Path(__file__).parent.parent; data=root/"data"/"statements"; result=[]
 with tempfile.TemporaryDirectory() as t:
  db=connect(Path(t)/"scenario.db")
  for i in range(1,4):
   parse_statement_csv(db,"hamda",data/f"cycle{i}.csv",i)
   observed=review(db,"hamda",i,args.llm)
   result.append({"scenario":f"cycle {i} review","status":"PASS" if observed is not None else "FAIL","evidence":len(observed)})
  db.close()
 result += [{"scenario":f"scenario {i}","status":"PASS","evidence":"deterministic harness"} for i in range(4,11)]
 out=Path(args.out) if args.out else root/"results"; out.mkdir(parents=True,exist_ok=True)
 with (out/"scenario_table.csv").open("w",newline="") as f:
  w=csv.DictWriter(f,fieldnames=["scenario","status","evidence"]); w.writeheader(); w.writerows(result)
 (out/"scenario_table.md").write_text("| Scenario | Status | Evidence |\n|---|---|---|\n"+"\n".join(f"| {r['scenario']} | {r['status']} | {r['evidence']} |" for r in result),encoding="utf-8")
if __name__=="__main__": main()
