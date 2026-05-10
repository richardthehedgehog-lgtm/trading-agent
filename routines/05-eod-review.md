# Routine 5: End-of-Day Review & Weekly Report

**Schedule:** 
- Daily: 5:00 PM ET (weekdays, after market close)
- Weekly: Sunday 6:00 PM ET (full weekly review)

**APIs:** Alpaca Paper Trading API, Perplexity API

## Daily End-of-Day Review

1. Fetch final account state from Alpaca: `GET /v2/account`
2. Fetch all closed orders for today: `GET /v2/orders?status=closed&after=TODAY`
3. Calculate:
   - Day's P&L ($ and %)
   - Portfolio vs SPY performance (fetch SPY daily change via Perplexity)
   - Running total P&L since inception
4. Write daily journal entry to `journal/YYYY-MM-DD.md`:
   - Market conditions today
   - Trades executed (entry, exit, reason)
   - P&L summary
   - Positions still open
   - Plan for tomorrow (any watchlist updates)
5. Update `memory/portfolio.json` with end-of-day snapshot
6. Reset `trading_paused: false` for next day (if it was set for daily loss limit — weekly limit requires Richard's review)

## Weekly Review (Sundays)

1. Compile the week's journal entries
2. Calculate weekly metrics:
   - Total return for the week
   - SPY return for the week
   - Alpha generated
   - Win rate (winning trades / total trades)
   - Average winner vs average loser
3. Review active positions — any thesis changes?
4. Update `memory/strategy.md` if lessons learned suggest adjustments
5. Write weekly summary to `journal/YYYY-WXX-weekly-review.md`
6. Post weekly summary to ClickUp task 86d2qf2cr as a comment

## Journal Entry Template

```markdown
# Trading Journal — [DATE]

## Market Overview
[Brief market summary from Perplexity]

## Trades Today
| Symbol | Action | Price | Size | Reason |
|--------|--------|-------|------|--------|
| AAPL   | BUY    | $185  | 27   | Momentum + AI tailwind |

## P&L
- Today: +$XXX (+X.X%)
- SPY today: +X.X%
- Running total: +$XXX (+X.X% since inception)

## Open Positions
[List with current P&L]

## Notes & Lessons
[What worked, what didn't, thesis updates]

## Plan for Tomorrow
[Watchlist additions/removals, levels to watch]
```

## Output
Writes to `journal/YYYY-MM-DD.md` (daily).
Writes to `journal/YYYY-WXX-weekly-review.md` (weekly).
Updates `memory/portfolio.json`.
Posts weekly summary to ClickUp.
