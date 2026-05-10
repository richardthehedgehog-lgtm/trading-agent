# Routine 2: Analyse Watchlist

**Schedule:** 9:00 AM ET (30 min before open)  
**Tool:** Perplexity API + Alpaca market data

## What This Routine Does

1. Read `memory/watchlist.json` and `memory/strategy.md`
2. For each stock on the watchlist:
   - Fetch latest price, volume, 52-week range via Alpaca
   - Check against strategy entry rules
   - Score each stock: Strong Buy / Buy / Hold / Sell / Strong Sell
3. Write analysis back to `memory/watchlist.json`
4. Flag top candidates for Routine 3 to act on

## Decision Logic

Apply rules from `memory/strategy.md`. If strategy is undefined, hold all positions.

## Output

Updates `memory/watchlist.json` with scores and reasoning.
