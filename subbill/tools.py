from __future__ import annotations
import csv, hashlib, re
from datetime import date, timedelta
from pathlib import Path
from .db import key, log, current_register, current_decision
from .policy import contains_untrusted, sanitize

ALIASES = {"netflix": "netflix", "spotify": "spotify", "icloud": "icloud", "gym": "gym",
           "electric": "electricity", "internet": "internet", "cloud": "cloud", "vps": "cloud",
           "notion": "notion", "adobe": "adobe"}
def merchant_key(description):
    text = description.lower()
    for token, merchant in ALIASES.items():
        if token in text: return merchant
    return "unknown_" + re.sub(r"\W+", "_", text).strip("_")[:30]

def parse_statement_csv(db, user_id, filename, cycle):
    data = Path(filename).read_bytes(); digest = hashlib.sha256(data).hexdigest()
    if db.execute("SELECT 1 FROM source_files WHERE user_id=? AND sha256=?", (user_id,digest)).fetchone():
        return 0
    with Path(filename).open(newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    required = {"date","description","amount","currency"}
    if not rows or not required <= set(rows[0]):
        raise ValueError("CSV must contain date, description, amount, currency")
    for idx, row in enumerate(rows, 1):
        desc = sanitize(row["description"]); memo = sanitize(row.get("memo",""))
        if contains_untrusted(desc + " " + memo): log(db, user_id, "safety", "UNTRUSTED_INSTRUCTION_DETECTED", cycle)
        db.execute("""INSERT OR IGNORE INTO transactions(user_id,cycle,file_sha256,row_ref,date,description,amount,merchant_key,memo)
                      VALUES(?,?,?,?,?,?,?,?,?)""", (user_id,cycle,digest,f"{Path(filename).name}#row{idx}",row["date"],desc,float(row["amount"]),merchant_key(desc),memo))
        merchant = merchant_key(desc)
        if not merchant.startswith("unknown_") and not db.execute(
                "SELECT 1 FROM register_items WHERE user_id=? AND merchant_key=?",
                (user_id, merchant)).fetchone():
            db.execute("INSERT INTO register_items(user_id,merchant_key,amount,interval,next_renewal,source_ref) VALUES(?,?,?,?,?,?)",
                       (user_id, merchant, float(row["amount"]), "monthly", row["date"], f"{Path(filename).name}#row{idx}"))
    db.execute("INSERT INTO source_files(user_id,sha256,name,version) VALUES(?,?,?,1)", (user_id,digest,Path(filename).name))
    db.commit(); log(db,user_id,"parse_statement_csv","ok",cycle); return len(rows)

def analyze_recurrence(db, user_id, cycle):
    rows = db.execute("SELECT merchant_key,amount,MIN(date) first_date,MAX(date) last_date,COUNT(*) n FROM transactions WHERE user_id=? AND cycle=? GROUP BY merchant_key", (user_id,cycle)).fetchall()
    issues=[]
    for r in rows:
        merchant=r["merchant_key"]; reg=db.execute("SELECT * FROM register_items WHERE user_id=? AND merchant_key=? AND status='current'",(user_id,merchant)).fetchone()
        if r["n"] > 1:
            issues.append(_issue(db,user_id,cycle,"DUPLICATE_CHARGE",merchant,f"Multiple charges in cycle {cycle}"))
        if not reg:
            typ = "UNKNOWN_MERCHANT" if merchant.startswith("unknown_") else None
            if typ: issues.append(_issue(db,user_id,cycle,typ,merchant,"Merchant has no register history"))
            continue
        if abs(float(reg["amount"])-float(r["amount"])) > 0.01:
            issues.append(_issue(db,user_id,cycle,"AMOUNT_CHANGED",merchant,f"Amount changed from {reg['amount']:.2f} to {r['amount']:.2f}"))
        decision=current_decision(db,user_id,merchant)
        if decision and decision["decision"]=="cancel":
            issues.append(_issue(db,user_id,cycle,"CANCELLED_STILL_BILLED",merchant,f"Billed after cancellation on {decision['decided_at'][:10]}"))
    db.commit(); return issues

def _issue(db,user,cycle,typ,merchant,detail):
    ident=key(user,cycle,typ,merchant,detail)
    db.execute("INSERT OR IGNORE INTO issues(user_id,cycle,type,merchant_key,detail,idempotency_key) VALUES(?,?,?,?,?,?)",(user,cycle,typ,merchant,detail,ident))
    return db.execute("SELECT * FROM issues WHERE idempotency_key=?",(ident,)).fetchone()

def add_evidence(db,user,merchant,note,source="manual"):
    db.execute("INSERT INTO evidence(user_id,merchant_key,note,source_ref) VALUES(?,?,?,?)",(user,merchant,sanitize(note),source)); db.commit()

def decide(db,user,merchant,decision,reason):
    db.execute("UPDATE decisions SET status='superseded' WHERE user_id=? AND merchant_key=? AND status='current'",(user,merchant))
    db.execute("INSERT INTO decisions(user_id,merchant_key,decision,reason) VALUES(?,?,?,?)",(user,merchant,decision,sanitize(reason))); db.commit()

def correct(db,user,merchant,field,value,reason,confirm=False):
    if field not in {"renewal_date", "amount", "interval"}:
        raise ValueError("field must be renewal_date, amount, or interval")
    value = sanitize(value)
    db.execute(
        "INSERT INTO corrections(user_id,merchant_key,field,value,reason,confirmed) VALUES(?,?,?,?,?,?)",
        (user, merchant, field, value, sanitize(reason), int(confirm)),
    )
    if confirm:
        current = db.execute(
            "SELECT * FROM register_items WHERE user_id=? AND merchant_key=? AND status='current' ORDER BY version DESC LIMIT 1",
            (user, merchant),
        ).fetchone()
        if not current:
            raise ValueError(f"No current register item exists for {merchant}")
        values = {key: current[key] for key in ("amount", "interval", "next_renewal")}
        column = {"renewal_date": "next_renewal"}.get(field, field)
        values[column] = float(value) if field == "amount" else value
        db.execute("UPDATE register_items SET status='superseded' WHERE item_id=?", (current["item_id"],))
        db.execute(
            """INSERT INTO register_items(user_id,merchant_key,amount,interval,next_renewal,status,version,source_ref,supersedes_id)
               VALUES(?,?,?,?,?,'current',?,?,?)""",
            (user, merchant, values["amount"], values["interval"], values["next_renewal"],
             current["version"] + 1, f"correction:{field}", current["item_id"]),
        )
    db.commit()
    return {"status": "confirmed" if confirm else "proposed", "merchant": merchant, "field": field, "value": value}

def draft_cancellation(db,user,merchant):
    ident=key(user,merchant,"draft-cancellation")
    row=db.execute("SELECT body FROM drafts WHERE idempotency_key=?",(ident,)).fetchone()
    if row: return row["body"]
    body=f"UNSENT DRAFT - not sent anywhere\nSubject: Cancellation request for {merchant}\nPlease cancel my {merchant} subscription."
    db.execute("INSERT INTO drafts(user_id,merchant_key,body,idempotency_key) VALUES(?,?,?,?)",(user,merchant,body,ident)); db.commit(); return body
