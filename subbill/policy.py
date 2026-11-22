import re
from typing import Any

ALLOWED_ACTIONS = {"request_usage_evidence", "propose_keep", "propose_cancel",
                   "propose_review_later", "wait", "escalate"}
UNTRUSTED = re.compile(r"(ignore previous instructions|send email|recipient\s+\S+)", re.I)

def sanitize(value: str) -> str:
    return value.replace("\x00", "")[:2000]

def contains_untrusted(value: str) -> bool:
    return bool(UNTRUSTED.search(value))

def validate_decision(payload: Any, evidence_refs: set[str]) -> dict[str, Any]:
    if not isinstance(payload, dict) or payload.get("action") not in ALLOWED_ACTIONS:
        return {"action": "escalate", "rationale": "Invalid model response; manual review required.", "evidence_refs": []}
    refs = payload.get("evidence_refs", [])
    if not isinstance(refs, list) or not all(isinstance(x, str) and x in evidence_refs for x in refs):
        return {"action": "escalate", "rationale": "Model referenced unavailable evidence.", "evidence_refs": []}
    return {"action": payload["action"], "rationale": sanitize(str(payload.get("rationale", ""))), "evidence_refs": refs}

