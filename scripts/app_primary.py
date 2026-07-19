from flask import Flask, request, redirect, render_template_string
import psycopg2
import os

app = Flask(__name__)

DB_CONFIG = {
    "host": "localhost",
    "database": "drtest",
    "user": "drapp",
    "password": os.environ.get("DB_PASSWORD", "")
}

SITE_NAME = os.environ.get("SITE_NAME", "UNKNOWN-SITE")
SITE_IP = os.environ.get("SITE_IP", "unknown")

TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Nkabom Savings & Loans PLC</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600&family=Inter:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
  :root{
    --ledger-bg:#16302B; --paper:#F6F1E4; --paper-line:#E4DCC6;
    --gold:#C9A227; --ink:#2A2A22; --ink-soft:#5B5647;
    --deposit:#2F6B3F; --withdrawal:#8A4B2A;
  }
  *{box-sizing:border-box;}
  body{
    margin:0; background: radial-gradient(ellipse at top left, rgba(201,162,39,0.08), transparent 55%), var(--ledger-bg);
    min-height:100vh; font-family:'Inter',sans-serif; color:var(--ink); padding:56px 20px;
  }
  .passbook{
    max-width:720px; margin:0 auto; background:var(--paper); border-radius:2px;
    box-shadow: 0 30px 60px -20px rgba(0,0,0,0.55), 0 0 0 1px rgba(201,162,39,0.15);
    position:relative; overflow:hidden;
  }
  .passbook::before{
    content:""; position:absolute; left:0; top:0; bottom:0; width:10px;
    background:repeating-linear-gradient(180deg, var(--gold) 0 3px, transparent 3px 9px); opacity:0.55;
  }
  header.letterhead{ padding:38px 44px 28px 56px; border-bottom:2px solid var(--ink); position:relative; }
  .eyebrow{ font-family:'IBM Plex Mono',monospace; font-size:11px; letter-spacing:0.12em; text-transform:uppercase; color:var(--ink-soft); }
  h1{ font-family:'Fraunces',serif; font-weight:600; font-size:32px; margin:6px 0 4px; letter-spacing:-0.01em; }
  .tagline{ font-size:13px; color:var(--ink-soft); font-style:italic; font-family:'Fraunces',serif; }
  .stamp{
    position:absolute; right:40px; top:32px; width:118px; height:118px;
    border:3px solid {{ stamp_color }}; border-radius:50%; color:{{ stamp_color }};
    display:flex; flex-direction:column; align-items:center; justify-content:center;
    transform:rotate(-11deg); font-family:'IBM Plex Mono',monospace; text-align:center;
    mix-blend-mode:multiply; opacity:0.92;
  }
  .stamp::before{ content:""; position:absolute; inset:6px; border:1px solid {{ stamp_color }}; border-radius:50%; opacity:0.6; }
  .stamp .s-top{ font-size:9px; letter-spacing:0.14em; margin-bottom:3px;}
  .stamp .s-main{ font-size:15px; font-weight:600; letter-spacing:0.03em; line-height:1.15;}
  .stamp .s-bottom{ font-size:8px; letter-spacing:0.1em; margin-top:3px;}
  section.body{ padding:30px 44px 40px 56px; }
  .section-label{
    font-family:'IBM Plex Mono',monospace; font-size:11px; text-transform:uppercase; letter-spacing:0.1em;
    color:var(--ink-soft); margin:0 0 14px; display:flex; align-items:center; gap:10px;
  }
  .section-label::after{ content:""; flex:1; height:1px; background:var(--paper-line); }
  .ledger{ width:100%; border-collapse:collapse; margin-bottom:36px;}
  .ledger th{
    text-align:left; font-family:'IBM Plex Mono',monospace; font-size:10px; text-transform:uppercase;
    letter-spacing:0.08em; color:var(--ink-soft); padding:0 10px 8px; font-weight:500;
  }
  .ledger th.num, .ledger td.num{ text-align:right; }
  .ledger tr.row{ border-top:1px solid var(--paper-line); }
  .ledger td{ padding:12px 10px; font-size:14px; vertical-align:middle;}
  .ledger td.acct{ font-family:'Fraunces',serif; font-size:15.5px; }
  .ledger td.amt{ font-family:'Fraunces',serif; font-variant-numeric:tabular-nums; font-weight:600; font-size:16px; }
  .tag{ display:inline-block; font-family:'IBM Plex Mono',monospace; font-size:10px; letter-spacing:0.05em; padding:2px 7px; border-radius:2px; text-transform:uppercase; }
  .tag.deposit{ background:rgba(47,107,63,0.12); color:var(--deposit); }
  .tag.withdrawal{ background:rgba(138,75,42,0.12); color:var(--withdrawal); }
  .ledger td.time{ font-family:'IBM Plex Mono',monospace; font-size:11px; color:var(--ink-soft); }
  form.entry{ background:rgba(0,0,0,0.02); border:1px solid var(--paper-line); border-radius:3px; padding:22px 24px; }
  .field-row{ display:flex; gap:14px; margin-bottom:14px; flex-wrap:wrap;}
  .field{ flex:1; min-width:150px; display:flex; flex-direction:column; gap:6px;}
  .field label{ font-family:'IBM Plex Mono',monospace; font-size:10px; text-transform:uppercase; letter-spacing:0.08em; color:var(--ink-soft); }
  .field input, .field select{
    font-family:'Inter',sans-serif; font-size:14px; padding:9px 10px; border:1px solid var(--paper-line);
    border-radius:2px; background:var(--paper); color:var(--ink);
  }
  .field input:focus, .field select:focus{ outline:2px solid var(--gold); outline-offset:1px; }
  button.submit{
    font-family:'IBM Plex Mono',monospace; font-size:12px; letter-spacing:0.08em; text-transform:uppercase;
    background:var(--ink); color:var(--paper); border:none; padding:11px 22px; border-radius:2px; cursor:pointer;
  }
  button.submit:hover{ background:#000; }
  footer{
    padding:16px 56px 22px; font-family:'IBM Plex Mono',monospace; font-size:10px;
    color:var(--ink-soft); letter-spacing:0.04em; border-top:1px solid var(--paper-line);
  }
</style>
</head>
<body>
  <div class="passbook">
    <header class="letterhead">
      <div class="eyebrow">Deposit &amp; Transaction Passbook</div>
      <h1>Nkabom Savings &amp; Loans PLC</h1>
      <div class="tagline">"Nkabom" &mdash; unity, togetherness.</div>
      <div class="stamp">
        <span class="s-top">Serving From</span>
        <span class="s-main">{{ site_name }}</span>
        <span class="s-bottom">{{ site_ip }}</span>
      </div>
    </header>
    <section class="body">
      <p class="section-label">Ledger &mdash; Recent Entries</p>
      <table class="ledger">
        <tr><th>Account</th><th>Type</th><th class="num">Amount (GHS)</th><th>Recorded</th></tr>
        {% for t in transactions %}
        <tr class="row">
          <td class="acct">{{ t[1] }}</td>
          <td><span class="tag {{ 'deposit' if t[3] == 'deposit' else 'withdrawal' }}">{{ t[3] }}</span></td>
          <td class="num amt">{{ "%.2f"|format(t[2]) }}</td>
          <td class="time">{{ t[4] }}</td>
        </tr>
        {% endfor %}
      </table>
      <p class="section-label">Record a Transaction</p>
      <form class="entry" method="POST" action="/add">
        <div class="field-row">
          <div class="field">
            <label>Account Name</label>
            <input name="account_name" placeholder="e.g. Yaa Asantewaa" required>
          </div>
          <div class="field">
            <label>Amount (GHS)</label>
            <input name="amount" type="number" step="0.01" placeholder="0.00" required>
          </div>
          <div class="field">
            <label>Type</label>
            <select name="transaction_type">
              <option value="deposit">Deposit</option>
              <option value="withdrawal">Withdrawal</option>
            </select>
          </div>
        </div>
        <button class="submit" type="submit">Record Entry</button>
      </form>
    </section>
    <footer>DR Failover Test Environment &mdash; CY384 Lab Project &mdash; University of Mines and Technology, Tarkwa</footer>
  </div>
</body>
</html>
"""

def get_connection():
    return psycopg2.connect(**DB_CONFIG)

@app.route("/")
def index():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, account_name, amount, transaction_type, created_at FROM transactions ORDER BY id DESC;")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    stamp_color = "#2F9E44" if "PRIMARY" in SITE_NAME.upper() else "#B33A3A"
    return render_template_string(TEMPLATE, transactions=rows, site_name=SITE_NAME, site_ip=SITE_IP, stamp_color=stamp_color)

@app.route("/add", methods=["POST"])
def add():
    account_name = request.form["account_name"]
    amount = request.form["amount"]
    transaction_type = request.form["transaction_type"]
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO transactions (account_name, amount, transaction_type) VALUES (%s, %s, %s);",
        (account_name, amount, transaction_type)
    )
    conn.commit()
    cur.close()
    conn.close()
    return redirect("/")

@app.route("/health")
def health():
    try:
        conn = get_connection()
        conn.close()
        return {"status": "ok", "site": SITE_NAME}, 200
    except Exception as e:
        return {"status": "error", "message": str(e)}, 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
