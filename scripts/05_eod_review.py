#!/usr/bin/env python3
"""
Routine 5: End-of-Day Journal & Weekly Review
Schedule: 7:00 AM AEST weekdays (= 5:00 PM ET)
          8:00 AM AEST Mondays (= Sunday 6 PM ET weekly review)
"""
import sys
sys.path.insert(0, str(__import__('pathlib').Path(__file__).parent))
from utils import *
import json
from datetime import date, timedelta

def run():
    log("=== ROUTINE 5: End-of-Day Review ===")
    
    portfolio = load_portfolio()
    
    try:
        client = get_alpaca_client()
        account = client.get_account()
        positions = client.get_all_positions()
        
        equity = float(account.equity)
        cash = float(account.cash)
        start_equity = portfolio.get("start_equity", 100000)
        todays_pnl = sum(float(p.unrealized_intraday_pl) for p in positions)
        total_pnl = equity - start_equity
        total_pnl_pct = (total_pnl / start_equity) * 100
        
        # Get closed orders today
        from alpaca.trading.requests import GetOrdersRequest
        from alpaca.trading.enums import QueryOrderStatus
        today_start = datetime.now().replace(hour=0, minute=0, second=0)
        orders_req = GetOrdersRequest(status=QueryOrderStatus.CLOSED, after=today_start, limit=50)
        todays_orders = client.get_orders(orders_req)
        
        log(f"EOD: equity=${equity:,.0f}, today P&L=${todays_pnl:+,.0f}, total={total_pnl_pct:+.2f}%")
        
    except Exception as e:
        log(f"Error fetching EOD data: {e}")
        equity = portfolio.get("total_equity", 100000)
        cash = portfolio.get("cash_balance", 100000)
        todays_pnl = portfolio.get("todays_pnl", 0)
        total_pnl = equity - portfolio.get("start_equity", 100000)
        total_pnl_pct = (total_pnl / portfolio.get("start_equity", 100000)) * 100
        todays_orders = []
        positions = []
    
    # Read today's journal so far
    journal_path = today_journal_path()
    existing_journal = journal_path.read_text() if journal_path.exists() else "No journal entries today."
    
    # Ask Claude to write a proper EOD summary
    pos_summary = "\n".join([
        f"- {p.symbol}: {float(p.qty)} shares, P&L {float(p.unrealized_plpc)*100:.1f}%"
        for p in positions
    ]) or "No open positions."
    
    orders_summary = "\n".join([
        f"- {o.symbol}: {o.side} {o.qty} @ ${o.filled_avg_price or 'N/A'} ({o.status})"
        for o in todays_orders
    ]) or "No orders today."
    
    prompt = f"""You are a disciplined stock trading agent writing the end-of-day journal.

**Today's Data:**
- Date: {date.today().isoformat()}
- Portfolio equity: ${equity:,.0f}
- Today's P&L: ${todays_pnl:+,.0f}
- Total P&L since inception: ${total_pnl:+,.0f} ({total_pnl_pct:+.2f}%)
- Cash: ${cash:,.0f}

**Today's Orders:**
{orders_summary}

**Open Positions:**
{pos_summary}

**Journal Entries From Today:**
{existing_journal[:2000]}

Write a concise EOD journal entry covering:
1. Brief market summary for the day
2. What we traded and why
3. P&L analysis  
4. What's still open and the thesis
5. Lessons learned / notes for tomorrow
6. Plan for tomorrow

Write in first person. Be honest about mistakes. Max 400 words."""
    
    log("Asking Claude to write EOD journal...")
    eod_summary = ask_claude(prompt, max_tokens=1500)
    
    # Write final journal entry
    append_journal(f"""### End of Day Summary (7:00 AM AEST)

{eod_summary or 'EOD summary generation failed.'}

---
**Stats:** Equity=${equity:,.0f} | Today={todays_pnl:+,.0f} | Total={total_pnl_pct:+.2f}%
""")
    
    # Update portfolio and reset daily P&L tracker
    portfolio["total_equity"] = equity
    portfolio["cash_balance"] = cash
    portfolio["todays_pnl"] = 0  # Reset for tomorrow
    portfolio["trading_paused"] = False  # Reset daily pause
    portfolio["positions"] = [
        {"symbol": p.symbol, "qty": float(p.qty), "unrealized_pl_pct": float(p.unrealized_plpc)*100}
        for p in positions
    ]
    save_portfolio(portfolio)
    
    # Regenerate dashboard data.json
    try:
        import subprocess as sp
        gen_script = BASE_DIR / "scripts" / "generate_dashboard.py"
        sp.run(["python3", str(gen_script)], capture_output=True, text=True)
        log("✅ Dashboard data regenerated.")
    except Exception as e:
        log(f"Dashboard generation failed: {e}")

    # Push updated journal + dashboard to GitHub
    try:
        import subprocess
        result = subprocess.run(
            ["git", "-C", str(BASE_DIR), "add", "journal/", "memory/", "docs/"],
            capture_output=True, text=True
        )
        result = subprocess.run(
            ["git", "-C", str(BASE_DIR), "commit", "-m",
             f"Trading journal {date.today().isoformat()} | P&L: ${todays_pnl:+,.0f}"],
            capture_output=True, text=True
        )
        subprocess.run(
            ["git", "-C", str(BASE_DIR), "push"],
            capture_output=True, text=True
        )
        log("✅ Journal + dashboard committed and pushed to GitHub.")
    except Exception as e:
        log(f"Git push failed: {e}")
    
    log(f"=== Routine 5 complete | Today: ${todays_pnl:+,.0f} | Total: {total_pnl_pct:+.2f}% ===")

if __name__ == "__main__":
    run()
