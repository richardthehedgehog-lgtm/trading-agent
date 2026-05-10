#!/usr/bin/env python3
"""
Routine 4: Monitor Positions (runs twice — midday and pre-close)
Schedule: 2:30 AM AEST (12:30 PM ET) and 5:50 AM AEST (3:50 PM ET)
"""
import sys
sys.path.insert(0, str(__import__('pathlib').Path(__file__).parent))
from utils import *
import json

def run():
    log("=== ROUTINE 4: Monitor Positions ===")
    
    portfolio = load_portfolio()
    
    try:
        client = get_alpaca_client()
        account = client.get_account()
        positions = client.get_all_positions()
        
        cash = float(account.cash)
        equity = float(account.equity)
        start_equity = portfolio.get("start_equity", 100000)
        
        # Calculate today's P&L
        todays_pnl = sum(float(p.unrealized_intraday_pl) for p in positions)
        total_pnl = equity - start_equity
        
        log(f"Account: equity=${equity:,.0f}, cash=${cash:,.0f}, today P&L=${todays_pnl:,.0f}")
        
        # Update portfolio state
        portfolio["total_equity"] = equity
        portfolio["cash_balance"] = cash
        portfolio["todays_pnl"] = todays_pnl
        portfolio["total_pnl"] = total_pnl
        portfolio["positions"] = [
            {
                "symbol": p.symbol,
                "qty": float(p.qty),
                "avg_entry": float(p.avg_entry_price),
                "current_price": float(p.current_price),
                "market_value": float(p.market_value),
                "unrealized_pl": float(p.unrealized_pl),
                "unrealized_pl_pct": float(p.unrealized_plpc) * 100
            }
            for p in positions
        ]
        save_portfolio(portfolio)
        
        # Check guardrails
        ok, reason = check_guardrails(portfolio)
        if not ok:
            log(f"⛔ Guardrail triggered: {reason}")
            # Close all positions on emergency stop
            if "EMERGENCY" in reason:
                log("EMERGENCY STOP — closing all positions!")
                for p in positions:
                    try:
                        client.close_position(p.symbol)
                        log(f"Closed {p.symbol}")
                    except Exception as e:
                        log(f"Error closing {p.symbol}: {e}")
            return
        
    except Exception as e:
        log(f"Error fetching account: {e}")
        return
    
    if not positions:
        log("No open positions to monitor.")
        return
    
    # Build position summary for Claude
    pos_summary = "\n".join([
        f"- {p.symbol}: {p.qty} shares @ ${float(p.avg_entry_price):.2f} entry, "
        f"now ${float(p.current_price):.2f} ({float(p.unrealized_plpc)*100:.1f}%)"
        for p in positions
    ])
    
    # Ask Claude what to do with each position
    is_preclose = datetime.now().hour >= 5  # 5AM AEST = 3PM ET approx
    timing = "PRE-CLOSE (10 minutes to market close)" if is_preclose else "MIDDAY CHECK"
    
    prompt = f"""You are a disciplined stock trading agent — {timing}.

**Open Positions:**
{pos_summary}

**Account:**
- Total equity: ${equity:,.0f}
- Today's P&L: ${todays_pnl:+,.0f}
- Cash available: ${cash:,.0f}

**Rules:**
- Stop-loss is -7% from entry (hard stop — should already be set)
- Consider taking profits if any position is +15% or more
- {"CLOSE any positions you don't want to hold overnight" if is_preclose else "Adjust stops if positions have moved significantly"}
- If a position has reversed thesis, close it

For each position, reply:
ACTION: HOLD or CLOSE or TRIM
SYMBOL: <ticker>
REASON: <one sentence>

Be disciplined. Don't hold losers hoping they recover. Do hold winners with intact thesis."""
    
    log(f"Asking Claude for position management ({timing})...")
    response = ask_claude(prompt, max_tokens=800)
    
    if response:
        log(f"Claude position decision:\n{response}")
        
        # Execute any CLOSE orders
        import re
        blocks = response.split("\n\n")
        for block in blocks:
            if "ACTION: CLOSE" not in block and "ACTION: TRIM" not in block:
                continue
            try:
                symbol = re.search(r'SYMBOL:\s*([A-Z]+)', block).group(1)
                action = "CLOSE" if "ACTION: CLOSE" in block else "TRIM"
                
                if action == "CLOSE":
                    client.close_position(symbol)
                    log(f"✅ Closed position: {symbol}")
                    
                    # Log the close
                    trade_log_path = MEMORY_DIR / "trade-log.jsonl"
                    with open(trade_log_path, "a") as f:
                        f.write(json.dumps({
                            "timestamp": datetime.now().isoformat(),
                            "action": "CLOSE",
                            "symbol": symbol,
                            "reason": "Claude decision"
                        }) + "\n")
            except Exception as e:
                log(f"Error closing {symbol}: {e}")
    
    append_journal(f"""### Position Monitor ({timing})

**Positions:**
{pos_summary}

**Today's P&L:** ${todays_pnl:+,.0f} | **Total P&L:** ${total_pnl:+,.0f}

**Claude's Actions:**
{response or 'N/A'}
""")
    
    log("=== Routine 4 complete ===")

if __name__ == "__main__":
    run()
