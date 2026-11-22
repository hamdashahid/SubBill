"""Restart-safe review orchestration. SQLite is the durable checkpoint store."""
from .llm import get_llm
from .tools import analyze_recurrence
def review(db,user,cycle,provider="mock",no_memory=False):
    issues=analyze_recurrence(db,user,cycle); llm=get_llm(provider); output=[]
    for issue in issues:
        evidence=[] if no_memory else db.execute("SELECT source_ref FROM evidence WHERE user_id=? AND merchant_key=?",(user,issue["merchant_key"])).fetchall()
        result=llm.decide(dict(issue),None,[x["source_ref"] for x in evidence])
        output.append({"issue_id":issue["issue_id"],"merchant":issue["merchant_key"],"type":issue["type"],"state":issue["status"],"recommended_action":result["action"],"rationale":result["rationale"],"evidence_refs":[x["source_ref"] for x in evidence],"approval":"yes" if result["action"] in {"propose_cancel","escalate"} else "no"})
    return output
