# Routine 4: Monitor Positions (Midday + Close)

**Schedule:** 12:30 PM ET (midday) AND 3:50 PM ET (pre-close) — weekdays
**APIs:** Alpaca Paper Trading API

## What This Routine Does

### At 12:30 PM (Midday Check)
1. Fetch all open positions from Alpaca: `GET /v2/positions`
2. Calculate current P&L for each position
3. Check daily loss guardrail (if total day P&L < -3% of equity → pause trading)
4. For winning positions (+10% or more): update stop-loss to break-even
5. For positions near -7% stop: verify stop order is still active
6. Log midday snapshot to today's journal

### At 3:50 PM (Pre-Close)
1. Re-check all positions
2. Decide: hold overnight or close?
   - **Close if:** momentum has clearly reversed, or thesis played out, or approaching profit target
   - **Hold if:** thesis still intact, stop-loss in place, not near earnings
3. Execute any close orders as limit orders (not market)
4. Update portfolio.json with end-of-day state
5. Calculate today's P&L vs start of day

## Alpaca API Calls

### Get All Positions
```
GET /v2/positions
```

### Update Stop-Loss (trailing stop adjustment)
```
PATCH /v2/orders/{order_id}  // Cancel old stop
POST /v2/orders              // Place new stop at updated price
```

### Close a Position
```
DELETE /v2/positions/{symbol}
```

## Output
Updates `memory/portfolio.json` with current positions and P&L.
Logs midday/close snapshot to `journal/YYYY-MM-DD.md`.
Sets `trading_paused: true` in portfolio.json if daily loss guardrail triggered.
