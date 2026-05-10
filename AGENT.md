# 24/7 AI Trading Agent — Claude Code Routines

> Built from Nate Herk's tutorial: https://youtu.be/6MC1XqZSltw  
> ClickUp task: 86d2qf2cr

## Overview

Autonomous stock trading agent running 5 Claude Code cloud routines on a schedule.
All state is persisted in `memory/` so each routine picks up where the last left off.

## Build Status

- [x] ~~Alpaca paper trading account created~~ ✅
- [x] ~~Strategy documented~~ ✅ (`memory/strategy.md`)
- [x] ~~Guardrails defined~~ ✅ (`config/guardrails.md`)
- [x] ~~Perplexity API key obtained~~ ✅
- [x] ~~Claude Code project + memory architecture~~ ✅ (this folder)
- [x] ~~All 5 routines documented~~ ✅ (`routines/`)
- [ ] GitHub private repo created and project pushed
- [ ] Claude Code cloud routines configured (5 routines)
- [ ] API keys added to Claude Code cloud environment
- [ ] All 5 routines tested with "Run Now"
- [ ] Go live!

## Project Structure

```
trading-agent/
├── AGENT.md                    ← Project overview + status
├── SOUL.md                     ← Agent identity and principles
├── AGENTS.md                   ← Operational instructions
├── MEMORY.md                   ← Long-term persistent memory
├── STRATEGY.md                 ← Trading strategy (also in memory/)
├── GUARDRAILS.md               ← Hard rules (also in config/)
├── memory/
│   ├── portfolio.json          ← Current positions, cash, P&L
│   ├── watchlist.json          ← Stocks under consideration
│   ├── strategy.md             ← Strategy rules
│   ├── market-context.md       ← Latest market research
│   └── trade-log.jsonl         ← Append-only trade history
├── routines/
│   ├── 01-market-research.md   ← Pre-market research (8:30 AM ET)
│   ├── 02-analyse-watchlist.md ← Analyse candidates (9:30 AM ET)
│   ├── 03-execute-trades.md    ← Execute trades (10:00 AM ET)
│   ├── 04-monitor-positions.md ← Monitor + close (12:30 + 3:50 PM ET)
│   └── 05-eod-review.md        ← EOD journal + weekly report
├── config/
│   ├── api-keys.md             ← Key status checklist
│   └── guardrails.md           ← Risk limits
├── journal/                    ← Daily + weekly trading journals
└── logs/                       ← Routine execution logs
```

## Next Step
Push this project to a private GitHub repo, then set up the 5 Claude Code cloud routines.
