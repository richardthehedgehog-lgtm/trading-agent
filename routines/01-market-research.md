# Routine 1: Morning Market Research

**Schedule:** 8:30 AM ET (before market open)  
**Tool:** Perplexity API (`PERPLEXITY_API_KEY`)

## What This Routine Does

1. Query Perplexity for today's market overview:
   - S&P 500 / NASDAQ pre-market futures
   - Top movers and news
   - Macro events (Fed decisions, earnings, CPI, etc.)
   - Sector sentiment

2. Write a brief summary to `memory/market-context.md`

3. Flag any high-impact events that should pause trading today

## Prompt Template

```
Search for today's market overview for [DATE]:
1. US pre-market futures (S&P 500, NASDAQ, DOW)
2. Top 5 movers with reasons
3. Key macro events today (earnings, Fed, economic data)
4. Overall market sentiment (risk-on / risk-off)
Keep it concise — 200 words max.
```

## Output

Updates `memory/market-context.md` with timestamped summary.
Sets `trading_paused: true` in portfolio.json if high-risk day detected.
