#!/usr/bin/env python3
"""
Routine 3: Execute Trades
Schedule: 11:45 PM AEST weekdays (= 9:45 AM ET, 15min after open)
"""
import sys
sys.path.insert(0, str(__import__('pathlib').Path(__file__).parent))
from utils import *
import json, re

def run():
    log("=== ROUTINE 3: Execute Trades ===")
    
    portfolio = load_portfolio()
    ok, reason = check_guardrails(portfolio)
    if not ok:
        log(f"⛔ Halting — {reason}")
        return
    
    watchlist = load_watchlist()
    candidates_text = watchlist.get("todays_candidates", "")
    symbols = watchlist.get("stocks", [])
    
    if not symbols:
        log("No candidates on watchlist. Skipping trade execution.")
        return
    
    # Get live account state from Alpaca
    try:
        client = get_alpaca_client()
        account = client.get_account()
        cash = float(account.cash)
        equity = float(account.equity)
        positions = client.get_all_positions()
        held_symbols = [p.symbol for p in positions]
        position_count = len(positions)
        log(f"Account: cash=${cash:,.0f}, equity=${equity:,.0f}, positions={position_count}")
    except Exception as e:
        log(f"Could not fetch account: {e}")
        return
    
    # Guardrail: max 10 positions
    if position_count >= 10:
        log("⛔ Max positions (10) reached. No new trades.")
        return
    
    # Guardrail: max 50% deployed
    if (equity - cash) / equity > 0.5:
        log("⛔ 50% portfolio deployment limit reached. No new trades.")
        return
    
    # Get live prices for candidates
    try:
        from alpaca.data.historical import StockHistoricalDataClient
        from alpaca.data.requests import StockLatestQuoteRequest
        alpaca_cfg, _ = load_config()
        data_client = StockHistoricalDataClient(
            api_key=alpaca_cfg["api_key"],
            secret_key=alpaca_cfg["secret_key"]
        )
        quote_req = StockLatestQuoteRequest(symbol_or_symbols=symbols)
        quotes = data_client.get_stock_latest_quote(quote_req)
        price_info = {s: float(quotes[s].ask_price) for s in symbols if s in quotes}
        log(f"Live prices: {price_info}")
    except Exception as e:
        log(f"Could not fetch prices: {e}")
        price_info = {}
    
    # Ask Claude for final go/no-go on each candidate
    price_str = "\n".join([f"- {s}: ${p:.2f}" for s, p in price_info.items()])
    
    prompt = f"""You are a disciplined stock trading agent. Market has been open 15 minutes.

**Watchlist candidates from pre-market:**
{candidates_text}

**Live prices right now:**
{price_str}

**Account state:**
- Available cash: ${cash:,.0f}
- Open positions: {position_count}/10
- Already holding: {held_symbols or 'nothing'}

**Position sizing:** Max $5,000 per trade (~5% of portfolio)

For each candidate, decide: BUY or SKIP.
Skip if: price moved too much from expected, or market opened poorly, or you have doubts.

Reply in this EXACT format for each stock:
ACTION: BUY or SKIP
SYMBOL: <ticker>
LIMIT_PRICE: <price to set limit order at>
QUANTITY: <shares — keep total value ≤ $5000>
STOP_PRICE: <7% below limit price>
REASON: <one sentence>

Be conservative. It's fine to buy nothing if conditions aren't right."""
    
    log("Asking Claude for trade execution decisions...")
    response = ask_claude(prompt, max_tokens=1000)
    
    if not response:
        log("No response from Claude.")
        return
    
    log(f"Claude execution decision:\n{response}")
    
    # Parse and execute BUY orders
    trades_executed = []
    blocks = response.split("\n\n")
    
    for block in blocks:
        if "ACTION: BUY" not in block:
            continue
        
        try:
            symbol = re.search(r'SYMBOL:\s*([A-Z]+)', block).group(1)
            limit_price = float(re.search(r'LIMIT_PRICE:\s*([\d.]+)', block).group(1))
            quantity = int(re.search(r'QUANTITY:\s*(\d+)', block).group(1))
            stop_price = float(re.search(r'STOP_PRICE:\s*([\d.]+)', block).group(1))
            
            if symbol in held_symbols:
                log(f"⚠️  Already holding {symbol}, skipping.")
                continue
            
            order_value = limit_price * quantity
            if order_value > 5500:  # Allow tiny overage for rounding
                log(f"⚠️  {symbol} order ${order_value:.0f} exceeds $5,000 limit. Skipping.")
                continue
            
            # Place limit buy order
            from alpaca.trading.requests import LimitOrderRequest, StopOrderRequest
            from alpaca.trading.enums import OrderSide, TimeInForce
            
            buy_order = LimitOrderRequest(
                symbol=symbol,
                qty=quantity,
                side=OrderSide.BUY,
                type="limit",
                time_in_force=TimeInForce.DAY,
                limit_price=round(limit_price, 2)
            )
            
            result = client.submit_order(buy_order)
            log(f"✅ BUY order placed: {quantity} x {symbol} @ ${limit_price:.2f} (order: {result.id})")
            
            # Place stop-loss order (GTC)
            stop_order = StopOrderRequest(
                symbol=symbol,
                qty=quantity,
                side=OrderSide.SELL,
                type="stop",
                time_in_force=TimeInForce.GTC,
                stop_price=round(stop_price, 2)
            )
            stop_result = client.submit_order(stop_order)
            log(f"🛡️  Stop-loss set: {symbol} @ ${stop_price:.2f} (order: {stop_result.id})")
            
            trades_executed.append({
                "symbol": symbol,
                "qty": quantity,
                "limit_price": limit_price,
                "stop_price": stop_price,
                "order_id": str(result.id)
            })
            
        except Exception as e:
            log(f"Error executing trade: {e}")
            continue
    
    # Append to trade log
    if trades_executed:
        trade_log_path = MEMORY_DIR / "trade-log.jsonl"
        with open(trade_log_path, "a") as f:
            for trade in trades_executed:
                trade["timestamp"] = datetime.now().isoformat()
                trade["action"] = "BUY"
                f.write(json.dumps(trade) + "\n")
    
    append_journal(f"""### Trade Execution (11:45 PM AEST)

**Claude's Decision:**
{response}

**Trades Placed:** {len(trades_executed)}
{json.dumps(trades_executed, indent=2) if trades_executed else 'None'}
""")
    
    log(f"=== Routine 3 complete — {len(trades_executed)} trade(s) placed ===")

if __name__ == "__main__":
    run()
