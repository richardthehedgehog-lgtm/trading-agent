#!/usr/bin/env python3
"""
Routine 1: Pre-market Research
Schedule: 8:00 PM AEST weekdays (= 6:00 AM ET)
"""
import sys
sys.path.insert(0, str(__import__('pathlib').Path(__file__).parent))
from utils import *
from datetime import date

def run():
    log("=== ROUTINE 1: Pre-Market Research ===")
    
    today = date.today().isoformat()
    
    # Research today's market via Perplexity
    log("Querying Perplexity for market overview...")
    try:
        market_query = f"""Today is {today}. Provide a concise pre-market overview:
1. US pre-market futures (S&P 500, NASDAQ, DOW) — direction and % change
2. Top 5 market-moving stories right now
3. Key economic events today (Fed speeches, earnings, CPI, etc.)
4. Overall risk sentiment (risk-on or risk-off?)
5. Any sectors showing unusual strength or weakness?
Keep it under 300 words. Be specific with numbers."""
        
        market_summary = perplexity_search(market_query)
        log("Market research complete.")
    except Exception as e:
        log(f"Perplexity error: {e}")
        market_summary = f"[Research failed: {e}]"
    
    # Save to memory
    context_path = MEMORY_DIR / "market-context.md"
    context_path.write_text(f"""# Market Context — {today}
*Updated: {datetime.now().strftime('%H:%M AEST')}*

## Pre-Market Overview
{market_summary}
""")
    log(f"Market context saved to {context_path}")
    
    # Ask Claude if we should trade today
    portfolio = load_portfolio()
    
    trading_decision = ask_claude(f"""You are a disciplined stock trading agent.

Today's market research:
{market_summary}

Current portfolio state:
- Cash: ${portfolio.get('cash_balance', 100000):,.0f}
- Equity: ${portfolio.get('total_equity', 100000):,.0f}
- Open positions: {len(portfolio.get('positions', []))}

Based on this pre-market overview, should we trade today?
- If market conditions look dangerous (high volatility event, major uncertainty), recommend PAUSE
- Otherwise recommend PROCEED

Reply with exactly one line:
DECISION: PROCEED or PAUSE
REASON: <one sentence why>""")
    
    if trading_decision:
        log(f"Claude trading decision: {trading_decision}")
        if "PAUSE" in trading_decision.upper():
            portfolio["trading_paused"] = True
            save_portfolio(portfolio)
            log("⚠️  Trading paused for today based on market conditions.")
        else:
            portfolio["trading_paused"] = False
            save_portfolio(portfolio)
            log("✅ Proceeding with trading today.")
    
    # Journal entry
    append_journal(f"""### Pre-Market Research (8PM AEST)

**Market Summary:**
{market_summary}

**Trading Decision:** {trading_decision or 'N/A'}
""")
    
    log("=== Routine 1 complete ===")

if __name__ == "__main__":
    run()
