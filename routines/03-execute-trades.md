# Routine 3: Execute Trades

**Schedule:** 10:00 AM ET (weekdays, after 9:45 AM minimum wait)
**APIs:** Alpaca Paper Trading API

## What This Routine Does

1. Read `memory/watchlist.json` for stocks flagged "approved_to_buy"
2. Read `memory/portfolio.json` — check current cash, positions, guardrails
3. For each approved stock:
   - Verify guardrails are not triggered (pause if daily loss limit hit)
   - Verify max positions not exceeded
   - Calculate position size (max 5% of equity)
   - Place LIMIT order at current ask price
   - Immediately set stop-loss order at -7% from entry
4. Log every order attempt (success or failure) to `memory/trade-log.jsonl`
5. Update `memory/portfolio.json` with new positions

## Alpaca API Calls

### Place Limit Buy Order
```
POST /v2/orders
{
  "symbol": "AAPL",
  "qty": 10,
  "side": "buy",
  "type": "limit",
  "time_in_force": "day",
  "limit_price": 185.00
}
```

### Place Stop-Loss Order (immediately after buy fills)
```
POST /v2/orders
{
  "symbol": "AAPL",
  "qty": 10,
  "side": "sell",
  "type": "stop",
  "time_in_force": "gtc",
  "stop_price": 172.05  // entry price * 0.93 (7% stop)
}
```

## Guardrail Checks Before ANY Trade
- [ ] trading_paused is false
- [ ] emergency_stop is false
- [ ] Current open positions < 10
- [ ] Cash available >= position size
- [ ] Portfolio deployed < 50% of equity
- [ ] Time is between 9:45 AM and 3:50 PM ET

## Output
Updates `memory/trade-log.jsonl` with each order.
Updates `memory/portfolio.json` with new positions.
