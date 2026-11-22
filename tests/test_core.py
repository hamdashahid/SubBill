import csv
from subbill.db import connect
from subbill.tools import parse_statement_csv, add_evidence, decide, draft_cancellation, correct
from subbill.policy import validate_decision
def statement(tmp_path):
 p=tmp_path/"x.csv"
 with p.open("w",newline="") as f:
  w=csv.DictWriter(f,fieldnames=["date","description","amount","currency"]); w.writeheader(); w.writerow({"date":"2026-01-01","description":"Netflix","amount":"15.99","currency":"USD"})
 return p
def test_ingest_idempotent_and_isolated(tmp_path):
 db=connect(tmp_path/"x.db"); p=statement(tmp_path)
 assert parse_statement_csv(db,"hamda",p,1)==1; assert parse_statement_csv(db,"hamda",p,1)==0
 assert db.execute("SELECT count(*) FROM transactions").fetchone()[0]==1
 assert db.execute("SELECT count(*) FROM transactions WHERE user_id='alex'").fetchone()[0]==0
def test_decision_and_draft_idempotent(tmp_path):
 db=connect(tmp_path/"x.db"); decide(db,"hamda","gym","cancel","not used")
 a=draft_cancellation(db,"hamda","gym"); b=draft_cancellation(db,"hamda","gym")
 assert a==b and a.startswith("UNSENT DRAFT")
def test_policy_fallback():
 result=validate_decision({"action":"bad","evidence_refs":[]},set())
 assert result["action"]=="escalate"

def test_correction_proposal_and_confirmation_supersede_register(tmp_path):
 db=connect(tmp_path/"x.db"); p=statement(tmp_path)
 parse_statement_csv(db,"hamda",p,1)
 proposed=correct(db,"hamda","netflix","renewal_date","2026-11-05","confirmed by provider")
 assert proposed["status"]=="proposed"
 correct(db,"hamda","netflix","renewal_date","2026-11-05","confirmed by provider",confirm=True)
 current=db.execute("SELECT next_renewal,version FROM register_items WHERE user_id=? AND merchant_key=? AND status='current'",("hamda","netflix")).fetchone()
 assert current["next_renewal"]=="2026-11-05" and current["version"]==2
