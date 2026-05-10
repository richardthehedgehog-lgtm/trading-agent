#!/usr/bin/env python3
"""
Routine 2: Analyse Watchlist & Identify Trades
Schedule: 11:30 PM AEST weekdays (= 9:30 AM ET, just before market open)
"""
import sys
sys.path.insert(0, str(__import__('pathlib').Path(__file__).parent))
from utils import *
import json

def run():
    log("=== ROUTINE 2: Analyse Watchlist ===")
    
    portfolio = load_portfolio()
    ok, reason = check_guardrails(portfolio)
    if not ok:
        log(f"⛔ Halting — {reason}")
        return
    
    # Load current market context
    context_path = MEMORY_DIR / "market-context.md"
    market_context = context_path.read_text() if context_path.exists() else "No market context available."
    
    # Load strategy
    strategy_path = MEMORY_DIR / "strategy.md"
    strategy = strategy_path.read_text() if strategy_path.exists() else ""
    
    # Get current Alpaca positions (to avoid duplicates)
    try:
        client = get_alpaca_client()
        positions = client.get_all_positions()
        held_symbols = [p.symbol for p in positions]
        log(f"Currently holding: {held_symbols or 'nothing'}")
    except Exception as e:
        log(f"Could not fetch positions: {e}")
        held_symbols = []
    
    # Ask Claude to identify 3-5 trade candidates
    prompt = f"""You are a disciplined stock trading agent. It is pre-market and the US market opens in 15 minutes.

**Today's Market Context:**
{market_context}

**Trading Strategy:**
{strategy}

**Currently Held Positions:** {held_symbols or 'None'}

**Task:** Identify 3-5 stocks to watch for potential entry today.

Rules:
- Large/mid-cap US stocks only (market cap > $2B)
- Must be above their 50-day moving average
- No earnings in the next 3 days
- No stocks already held
- Max 5% of portfolio per position (~$5,000)

For each candidate, provide:
SYMBOL: <ticker>
THESIS: <one sentence why>
ENTRY_AROUND: <approximate price level>
STOP_LOSS: <7% below entry>
TARGET: <15-20% above entry>

List only genuine opportunities. If market conditions are poor, list NONE and explain why."""
    
    log("Asking Claude for trade candidates...")
    response = ask_claude(prompt, max_tokens=1500)
    
    if not response:
        log("No response from Claude.")
        return
    
    log(f"Claude response:\n{response}")
    
    # Parse candidates into watchlist
    watchlist = load_watchlist()
    
    # Reset today's candidates
    watchlist["todays_candidates"] = response
    watchlist["updated_at"] = datetime.now().isoformat()
    
    # Extract symbols from response
    import re
    symbols = re.findall(r'SYMBOL:\s*([A-Z]{1,5})', response)
    watchlist["stocks"] = symbols
    save_watchlist(watchlist)
    
    log(f"Watchlist updated: {symbols}")
    
    append_journal(f"""### Watchlist Analysis (11:30 PM AEST)

**Trade Candidates:**
{response}

**Symbols to watch:** {symbols}
""")
    
    log("=== Routine 2 complete ===")

if __name__ == "__main__":
    run()
