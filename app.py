import os
from pathlib import Path
import tempfile
import pandas as pd
from datetime import date, timedelta
import streamlit as st
from subbill.db import connect,current_register
from subbill.tools import parse_statement_csv,analyze_recurrence,add_evidence,decide,draft_cancellation
from subbill.graph import review
from subbill.export import export_register
ROOT=Path(__file__).parent
st.set_page_config(page_title='SubBill | Personal Finance',page_icon='🧾',layout='wide')
st.markdown('''<style>.block-container{padding-top:1.8rem}.metric-card{background:#f4f6fb;padding:18px;border-radius:14px}</style>''',unsafe_allow_html=True)
st.title('🧾 SubBill')
st.caption('Subscription & Bill Assistant · D03 · SQLite-backed personal billing memory')
with st.sidebar:
 st.subheader('Workspace'); user=st.text_input('User ID',value='hamda'); db_path=st.text_input('SQLite database',value=os.getenv('DATABASE_PATH',str(ROOT/'subbill.db')))
 provider=st.selectbox('Decision model',['mock','groq']); cycle=st.number_input('Billing cycle',1,120,1)
 st.caption('No payments, cancellations, or emails are executed. All decisions require your approval.')
db=connect(db_path)
tabs=st.tabs(['Dashboard','Statement Upload','Agent Review','Subscription Register','Usage Evidence','Cancellation Drafts','Activity & Memory','Demo / Restart'])
with tabs[0]:
 reg=[dict(x) for x in current_register(db,user)]; issues=[dict(x) for x in db.execute("SELECT * FROM issues WHERE user_id=? AND status='open' ORDER BY issue_id DESC",(user,))]
 monthly=sum(float(x['amount']) for x in reg if x['interval']=='monthly')
 upcoming=sum(1 for x in reg if x['next_renewal'] and date.today() <= date.fromisoformat(x['next_renewal']) <= date.today()+timedelta(days=30))
 counts={kind:sum(1 for x in issues if x['type']==kind) for kind in ['DUPLICATE_CHARGE','AMOUNT_CHANGED','CANCELLED_STILL_BILLED']}
 a,b,c=st.columns(3); a.metric('Monthly recurring',f'${monthly:,.2f}'); b.metric('Active subscriptions',len(reg)); c.metric('Upcoming renewals · 30 days',upcoming)
 a,b,c=st.columns(3); a.metric('Potential duplicates',counts['DUPLICATE_CHARGE']); b.metric('Amount changes',counts['AMOUNT_CHANGED']); c.metric('Cancelled but billed',counts['CANCELLED_STILL_BILLED'])
 if issues: st.dataframe(pd.DataFrame(issues),use_container_width=True)
 else: st.success('No open billing findings for this user.')
with tabs[1]:
 up=st.file_uploader('Upload a bank/card statement CSV',type=['csv'])
 if up:
  try:
   frame=pd.read_csv(up); st.dataframe(frame,use_container_width=True)
   if st.button('Validate and process statement'):
    with tempfile.TemporaryDirectory() as temp_dir:
     path=Path(temp_dir)/Path(up.name).name; path.write_bytes(up.getvalue())
     count=parse_statement_csv(db,user,path,int(cycle))
    st.success(f'Processed {count} transaction rows. Re-uploading identical content is idempotent.')
  except Exception as e: st.error(f'CSV validation failed: {e}')
 st.caption('Required columns: date, description, amount, currency. Optional: memo.')
with tabs[2]:
 if st.button('Run LangGraph review',type='primary'):
  try: st.session_state['review_findings']=review(db,user,int(cycle),provider)
  except Exception as e: st.error(str(e))
 findings=st.session_state.get('review_findings',[])
 for f in findings:
  with st.expander(f"{f['merchant']} · {f['type']}",expanded=True):
   st.write('**Agent recommendation:**',f['recommended_action']); st.write(f['rationale']); st.write('**Retrieved evidence references:**',f['evidence_refs'] or 'No saved usage evidence')
   reason=st.text_input('Reason',key=f"reason_{f['issue_id']}")
   cols=st.columns(3)
   for col,label,val in zip(cols,['Keep','Cancel','Review later'],['keep','cancel','review_later']):
    if col.button(label,key=f"{val}_{f['issue_id']}"):
     if not reason.strip(): st.warning('Please provide a reason before recording your decision.')
     else: decide(db,user,f['merchant'],val,reason); st.success('Decision saved to persistent memory.')
with tabs[3]:
 allreg=[dict(x) for x in db.execute('SELECT * FROM register_items WHERE user_id=? ORDER BY merchant_key,version',(user,))]
 st.dataframe(pd.DataFrame(allreg),use_container_width=True)
 if allreg:
  merchant=st.selectbox('Merchant to export',sorted({x['merchant_key'] for x in allreg}))
  with st.expander('Propose a register correction'):
   field=st.selectbox('Field',['amount','renewal_date','interval']); value=st.text_input('New value'); why=st.text_input('Correction evidence / reason')
   if st.button('Save correction proposal'):
    from subbill.tools import correct
    try: st.json(correct(db,user,merchant,field,value,why,False))
    except Exception as e: st.error(str(e))
 if st.button('Export register snapshot'):
  rows=export_register(db,user,ROOT/'results'); st.success(f'Exported {len(rows)} rows to results/.')
with tabs[4]:
 known=sorted({x['merchant_key'] for x in current_register(db,user)})
 merchant=st.selectbox('Merchant',known or [''],key='evidence_merchant'); note=st.text_area('Usage evidence (e.g. last used, frequency, value)')
 if st.button('Add usage evidence'):
  if note.strip(): add_evidence(db,user,merchant,note); st.success('Evidence stored.')
 st.dataframe(pd.DataFrame([dict(x) for x in db.execute('SELECT * FROM evidence WHERE user_id=? ORDER BY added_at DESC',(user,))]),use_container_width=True)
with tabs[5]:
 m=st.text_input('Merchant for cancellation draft')
 if st.button('Generate UNSENT cancellation draft'):
  if m.strip(): st.session_state['draft']=draft_cancellation(db,user,m.strip())
 if 'draft' in st.session_state: st.warning('UNSENT — this text has not been sent anywhere.'); st.code(st.session_state['draft'])
 st.dataframe(pd.DataFrame([dict(x) for x in db.execute('SELECT merchant_key,label,body FROM drafts WHERE user_id=?',(user,))]),use_container_width=True)
with tabs[6]:
 for title,sql in [('Decisions','SELECT * FROM decisions WHERE user_id=? ORDER BY id DESC'),('Issues','SELECT * FROM issues WHERE user_id=? ORDER BY issue_id DESC'),('Tool/action logs','SELECT * FROM action_log WHERE user_id=? ORDER BY id DESC'),('Source files','SELECT * FROM source_files WHERE user_id=? ORDER BY ingested_at DESC')]:
  st.subheader(title); st.dataframe(pd.DataFrame([dict(x) for x in db.execute(sql,(user,))]),use_container_width=True)
with tabs[7]:
 st.info('SQLite is the persistent memory. Close this process and relaunch the app with the same database path to verify restart recovery.')
 st.subheader('Current register snapshot'); st.dataframe(pd.DataFrame([dict(x) for x in current_register(db,user)]),use_container_width=True)
 st.subheader('Cycle 3 historical decisions'); st.dataframe(pd.DataFrame([dict(x) for x in db.execute("SELECT merchant_key,decision,reason,decided_at FROM decisions WHERE user_id=? AND status='current'",(user,))]),use_container_width=True)
 if st.button('Export before/after restart evidence'):
  export_register(db,user,ROOT/'results'/'restart_evidence'); st.success('Snapshot exported. Restart the app and export again to compare.')
db.close()
