import csv, json
from pathlib import Path
def export_register(db, user, out_dir):
    out=Path(out_dir); out.mkdir(parents=True,exist_ok=True)
    rows=[dict(x) for x in db.execute("SELECT ? user_id,merchant_key,amount,interval,next_renewal,status,version FROM register_items WHERE user_id=? ORDER BY merchant_key",(user,user))]
    (out/"register.json").write_text(json.dumps({"note":"DB is authoritative; export is one-way.","rows":rows},indent=2),encoding="utf-8")
    with (out/"register.csv").open("w",newline="",encoding="utf-8") as f:
        writer=csv.DictWriter(f,fieldnames=["user_id","merchant_key","amount","interval","next_renewal","status","version"]); writer.writeheader(); writer.writerows(rows)
    return rows
