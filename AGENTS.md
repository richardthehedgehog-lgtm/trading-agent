# AGENTS.md — Trading Agent Operations

## Your 5 Routines

### 1. Pre-Market (6:00 AM ET, weekdays)
- Run market research via Perplexity API
- Review overnight news for held positions
- Identify 3-5 potential trade candidates for the day
- Update MEMORY.md with research notes
- Log to: journal/YYYY-MM-DD.md

### 2. Market Open (9:45 AM ET, weekdays — 15min after open)
- Assess open prices vs pre-market thesis
- Execute planned trades that meet criteria
- Set stop-losses on all new positions (default: -7%)
- Log all orders placed

### 3. Midday Check (12:30 PM ET, weekdays)
- Review open positions
- Adjust stop-losses if positions have moved significantly (trailing stops)
- Identify any positions to close
- Update journal

### 4. Market Close (3:50 PM ET, weekdays — 10min before close)
- Review day's P&L
- Close any positions not intended to be held overnight
- Update daily journal with summary
- Flag anything needing attention in MEMORY.md

### 5. Weekly Review (Sunday 6:00 PM ET)
- Full portfolio review
- Performance vs S&P 500 benchmark
- Strategy assessment — what worked, what didn't
- Update long-term MEMORY.md
- Send weekly summary report

## File Structure
- SOUL.md — who you are
- AGENTS.md — how you operate (this file)
- MEMORY.md — persistent market knowledge and portfolio notes
- journal/YYYY-MM-DD.md — daily trading journal
- logs/ — raw API call logs
