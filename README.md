# 24/7 AI Trading Agent 🤖📈

Autonomous stock trading agent using Claude Code Routines + Alpaca Paper Trading API.

**Based on:** [Nate Herk's tutorial](https://youtu.be/6MC1XqZSltw)

## What This Does
- Runs 5 scheduled cloud routines (no computer needs to be on)
- Researches markets via Perplexity AI
- Places trades via Alpaca API (paper mode - no real money)
- Journals every decision to markdown files
- Tracks performance vs S&P 500

## Routines Schedule (ET)
| Time | Routine |
|------|---------|
| 8:30 AM | Market research (Perplexity) |
| 10:00 AM | Execute trades |
| 12:30 PM | Monitor positions |
| 3:50 PM | Pre-close review |
| 5:00 PM | EOD journal |
| Sunday 6 PM | Weekly review |

## Status
🟡 Paper trading — no real money at risk

## Setup
See `config/api-keys.md` for required environment variables.
