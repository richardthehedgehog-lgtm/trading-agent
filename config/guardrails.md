# Trading Agent Guardrails — Hard Rules (No Exceptions)

**Last updated:** 2026-05-11 by Cheryl

## Risk Limits
- **Daily loss limit:** -3% of portfolio value (~$3,000 at start)
  - If daily P&L hits -3%: STOP all trading for the rest of the day. Log reason.
- **Weekly loss limit:** -5% of portfolio
  - If hit: pause trading and alert Richard. Wait for review before resuming.
- **Drawdown emergency stop:** If portfolio drops below $85,000 (-15% from $100k start):
  - HALT all trading immediately
  - Close all open positions
  - Log reason in detail
  - Alert Richard and await explicit instructions to resume

## Position Limits
- Max single position size: 5% of portfolio (~$5,000)
- Max concurrent open positions: 10
- Max portfolio deployed: 50% (always maintain ≥50% cash)
- Max positions in same sector: 3

## Trade Rules
- NEVER trade in first 15 minutes after market open (no trades before 9:45 AM ET)
- NEVER place market orders — limit orders ONLY
- NEVER hold a losing position past its -7% stop-loss
- NEVER trade a stock with earnings in the next 3 days
- NEVER trade based on social media hype without corroborating Perplexity research
- NEVER exceed position size limits, even if conviction is high

## Market Hours
- Only trade during regular market hours: 9:45 AM – 3:50 PM ET (Mon–Fri)
- No pre-market or after-market orders

## Blacklisted Symbols
- Penny stocks (price < $5)
- Leveraged ETFs (e.g., TQQQ, SOXL)
- OTC / pink sheet stocks
- Stocks with market cap < $2B

## Paper Trading Status
paper_trading_only: true
(Do not change without Richard's explicit instruction)

## Reporting
- Richard receives a daily journal entry every evening
- Any guardrail trigger must be logged AND an alert sent to Richard immediately
