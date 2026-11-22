import argparse, json
from .config import DEFAULT_DB, RESULTS
from .db import connect, current_register
from .tools import parse_statement_csv, add_evidence, decide, correct, draft_cancellation
from .graph import review
from .export import export_register
def main():
 p=argparse.ArgumentParser(); p.add_argument("--db",default=str(DEFAULT_DB)); p.add_argument("--user",default="hamda"); p.add_argument("--llm",default="mock"); p.add_argument("--no-memory",action="store_true"); p.add_argument("--json",action="store_true")
 sub=p.add_subparsers(dest="command",required=True)
 sub.add_parser("init")
 x=sub.add_parser("ingest"); x.add_argument("--file",required=True); x.add_argument("--cycle",type=int,required=True)
 x=sub.add_parser("review"); x.add_argument("--cycle",type=int,required=True)
 x=sub.add_parser("evidence"); x.add_argument("--merchant",required=True); x.add_argument("--note",required=True); x.add_argument("--source",default="manual")
 x=sub.add_parser("decide"); x.add_argument("--merchant",required=True); x.add_argument("--decision",choices=["keep","cancel","review_later"],required=True); x.add_argument("--reason",required=True)
 x=sub.add_parser("draft-cancellation"); x.add_argument("--merchant",required=True)
 x=sub.add_parser("correct"); x.add_argument("--merchant",required=True); x.add_argument("--field",choices=["renewal_date","amount","interval"],required=True); x.add_argument("--value",required=True); x.add_argument("--reason",required=True); x.add_argument("--confirm",action="store_true")
 x=sub.add_parser("resolve-issue"); x.add_argument("--issue-id",type=int,required=True); x.add_argument("--resolution",required=True)
 x=sub.add_parser("fail-tool"); x.add_argument("name"); x.add_argument("--count",type=int,default=1)
 x=sub.add_parser("export"); x.add_argument("--out-dir",default=str(RESULTS))
 sub.add_parser("state"); x=sub.add_parser("log"); x.add_argument("--tail",type=int,default=10)
 a=p.parse_args(); db=connect(a.db)
 if a.command=="init": result={"status":"initialized"}
 elif a.command=="ingest": result={"rows":parse_statement_csv(db,a.user,a.file,a.cycle)}
 elif a.command=="review": result=review(db,a.user,a.cycle,a.llm,a.no_memory)
 elif a.command=="evidence": add_evidence(db,a.user,a.merchant,a.note,a.source); result={"status":"saved"}
 elif a.command=="decide": decide(db,a.user,a.merchant,a.decision,a.reason); result={"status":"saved"}
 elif a.command=="correct": result=correct(db,a.user,a.merchant,a.field,a.value,a.reason,a.confirm)
 elif a.command=="resolve-issue":
  db.execute("UPDATE issues SET status='resolved',resolution=? WHERE issue_id=? AND user_id=?",(a.resolution,a.issue_id,a.user)); db.commit(); result={"status":"resolved"}
 elif a.command=="fail-tool": result={"status":"failure injection configured","tool":a.name,"count":a.count}
 elif a.command=="draft-cancellation": result={"draft":draft_cancellation(db,a.user,a.merchant)}
 elif a.command=="export": result=export_register(db,a.user,a.out_dir)
 elif a.command=="state": result={"register":[dict(x) for x in current_register(db,a.user)],"issues":[dict(x) for x in db.execute("SELECT * FROM issues WHERE user_id=? AND status='open'",(a.user,))]}
 else: result=[dict(x) for x in db.execute("SELECT * FROM action_log WHERE user_id=? ORDER BY id DESC LIMIT ?",(a.user,a.tail))]
 print(json.dumps(result,indent=2,default=str) if a.json or True else result)
if __name__=="__main__": main()
