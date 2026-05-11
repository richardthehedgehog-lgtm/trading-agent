#!/usr/bin/env python3
"""
Dashboard Data Generator
Reads journal files + Alpaca API → outputs docs/data.json
Called at end of each EOD routine (Routine 5)
"""
import sys, json, re, os
from pathlib import Path
from datetime import datetime, date

ROOT = Path(__file__).parent.parent
JOURNAL_DIR = ROOT / "journal"
DOCS_DIR = ROOT / "docs"
ALPACA_CONFIG = ROOT.parent / "alpaca_config.json"

def load_alpaca_config():
    if ALPACA_CONFIG.exists():
        return json.loads(ALPACA_CONFIG.read_text())
    return {}

def fetch_alpaca(endpoint):
    """Direct REST call to Alpaca (no SDK needed)."""
    import urllib.request
    cfg = load_alpaca_config()
    base = cfg.get("base_url", "https://paper-api.alpaca.markets/v2")
    url = f"{base}{endpoint}"
    req = urllib.request.Request(url, headers={
        "APCA-API-KEY-ID": cfg.get("api_key", ""),
        "APCA-API-SECRET-KEY": cfg.get("secret_key", ""),
    })
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.loads(r.read())
    except Exception as e:
        print(f"  [Alpaca API error: {e}]")
        return None

def parse_eod_journal(md_text):
    """Extract key metrics from an EOD journal markdown file."""
    result = {}

    # Portfolio line: **Portfolio:** $100,077 | **P&L Today:** +$77 | **Total:** +$77 (+0.08%) | **Cash:** $95,398
    m = re.search(r'\*\*Portfolio:\*\*\s*\$([\d,]+)', md_text)
    if m:
        result["equity"] = float(m.group(1).replace(",", ""))

    m = re.search(r'\*\*P&L Today:\*\*\s*[+-]?\$([\d,]+)', md_text)
    if m:
        result["pnl_today"] = float(m.group(1).replace(",", ""))
        if re.search(r'P&L Today:\*\*\s*-', md_text):
            result["pnl_today"] *= -1

    m = re.search(r'\*\*Total:\*\*\s*[+-]?\$([\d,]+)\s*\(([+-]?[\d.]+)%\)', md_text)
    if m:
        result["pnl_total"] = float(m.group(1).replace(",", ""))
        result["pnl_total_pct"] = float(m.group(2))
        if re.search(r'\*\*Total:\*\* -', md_text):
            result["pnl_total"] *= -1
            result["pnl_total_pct"] *= -1

    m = re.search(r'\*\*Cash:\*\*\s*\$([\d,]+)', md_text)
    if m:
        result["cash"] = float(m.group(1).replace(",", ""))

    # Extract summary (section 1 = Market Summary)
    m = re.search(r'## 1\. Market Summary\s*(.*?)(?=## 2\.)', md_text, re.DOTALL)
    if m:
        result["market_summary"] = m.group(1).strip()[:500]

    # Extract traded section
    m = re.search(r'## 2\. What We Traded\s*(.*?)(?=## 3\.)', md_text, re.DOTALL)
    if m:
        result["what_traded"] = m.group(1).strip()[:300]

    # Extract lessons
    m = re.search(r'## 5\. Lessons Learned\s*(.*?)(?=## 6\.)', md_text, re.DOTALL)
    if m:
        result["lessons"] = m.group(1).strip()[:400]

    # Extract plan for tomorrow
    m = re.search(r'## 6\. Plan for Tomorrow\s*(.*?)(?=---|$)', md_text, re.DOTALL)
    if m:
        result["plan"] = m.group(1).strip()[:400]

    return result

def parse_trade_execution(md_text, trade_date):
    """Extract BUY/SELL/SKIP decisions from trade execution section."""
    trades = []
    sections = re.findall(
        r'```\s*(ACTION:\s*\w+.*?)```',
        md_text, re.DOTALL
    )
    for s in sections:
        action_m = re.search(r'ACTION:\s*(\w+)', s)
        symbol_m = re.search(r'SYMBOL:\s*(\w+)', s)
        price_m  = re.search(r'LIMIT_PRICE:\s*([\d.]+)', s)
        qty_m    = re.search(r'QUANTITY:\s*(\d+)', s)
        stop_m   = re.search(r'STOP_PRICE:\s*([\d.]+)', s)
        reason_m = re.search(r'REASON:\s*(.*)', s, re.DOTALL)

        action = action_m.group(1) if action_m else "?"
        symbol = symbol_m.group(1) if symbol_m else "?"
        if symbol in ("N/A", "?"):
            continue

        trade = {
            "date": trade_date,
            "action": action,
            "symbol": symbol,
            "price": float(price_m.group(1)) if price_m and price_m.group(1) not in ("N/A",) else None,
            "qty": int(qty_m.group(1)) if qty_m and qty_m.group(1) not in ("N/A",) else None,
            "stop": float(stop_m.group(1)) if stop_m and stop_m.group(1) not in ("N/A",) else None,
            "reason": reason_m.group(1).strip()[:200] if reason_m else "",
        }
        trades.append(trade)
    return trades

def build_history_from_journals():
    """Walk all journal files, extract daily equity/P&L."""
    history = []
    trades = []
    journals = []

    for jf in sorted(JOURNAL_DIR.glob("*.md")):
        day = jf.stem  # e.g. "2026-05-12"
        text = jf.read_text()
        metrics = parse_eod_journal(text)
        day_trades = parse_trade_execution(text, day)

        if metrics:
            history.append({
                "date": day,
                "equity": metrics.get("equity", 100000),
                "pnl_today": metrics.get("pnl_today", 0),
                "pnl_total": metrics.get("pnl_total", 0),
                "pnl_total_pct": metrics.get("pnl_total_pct", 0),
                "cash": metrics.get("cash", 100000),
            })
            journals.append({
                "date": day,
                "equity": metrics.get("equity"),
                "pnl_today": metrics.get("pnl_today"),
                "pnl_total": metrics.get("pnl_total"),
                "pnl_total_pct": metrics.get("pnl_total_pct"),
                "market_summary": metrics.get("market_summary", ""),
                "what_traded": metrics.get("what_traded", ""),
                "lessons": metrics.get("lessons", ""),
                "plan": metrics.get("plan", ""),
                "full_text": text[:3000],
            })
        trades.extend(day_trades)

    return history, trades, journals

def get_live_positions():
    """Fetch live positions from Alpaca."""
    positions_raw = fetch_alpaca("/positions")
    account_raw   = fetch_alpaca("/account")

    positions = []
    if isinstance(positions_raw, list):
        for p in positions_raw:
            positions.append({
                "symbol":           p.get("symbol"),
                "qty":              float(p.get("qty", 0)),
                "entry_price":      float(p.get("avg_entry_price", 0)),
                "current_price":    float(p.get("current_price", 0)),
                "market_value":     float(p.get("market_value", 0)),
                "unrealized_pnl":   float(p.get("unrealized_pl", 0)),
                "unrealized_pnl_pct": float(p.get("unrealized_plpc", 0)) * 100,
                "side":             p.get("side", "long"),
            })

    account = {}
    if isinstance(account_raw, dict):
        account = {
            "equity":      float(account_raw.get("equity", 0)),
            "cash":        float(account_raw.get("cash", 0)),
            "buying_power": float(account_raw.get("buying_power", 0)),
            "today_pnl":   float(account_raw.get("equity", 0)) - float(account_raw.get("last_equity", account_raw.get("equity", 0))),
        }

    return positions, account

def get_recent_orders():
    """Fetch last 50 orders from Alpaca."""
    orders_raw = fetch_alpaca("/orders?status=all&limit=50&direction=desc")
    orders = []
    if isinstance(orders_raw, list):
        for o in orders_raw:
            orders.append({
                "id":        o.get("id"),
                "symbol":    o.get("symbol"),
                "side":      o.get("side"),
                "qty":       float(o.get("qty", 0)),
                "type":      o.get("type"),
                "status":    o.get("status"),
                "filled_at": o.get("filled_at"),
                "filled_avg_price": float(o.get("filled_avg_price") or 0),
                "submitted_at": o.get("submitted_at"),
            })
    return orders

def main():
    print("=== Generating dashboard data ===")
    DOCS_DIR.mkdir(exist_ok=True)

    # 1. History from journals
    history, trade_decisions, journals = build_history_from_journals()
    print(f"  Journal days: {len(history)}")

    # 2. Live data from Alpaca
    print("  Fetching Alpaca live data...")
    live_positions, account = get_live_positions()
    orders = get_recent_orders()

    # 3. Merge: use live account if available, else last journal entry
    if account:
        account_summary = {
            "equity":       account["equity"],
            "cash":         account["cash"],
            "buying_power": account["buying_power"],
            "today_pnl":    account["today_pnl"],
            "start_value":  100000.0,
            "start_date":   "2026-05-11",
            "total_pnl":    account["equity"] - 100000.0,
            "total_pnl_pct": ((account["equity"] - 100000.0) / 100000.0) * 100,
        }
        print(f"  Live account: ${account['equity']:,.0f}")
    elif history:
        last = history[-1]
        account_summary = {
            "equity":       last["equity"],
            "cash":         last.get("cash", 100000),
            "buying_power": last.get("cash", 100000),
            "today_pnl":    last["pnl_today"],
            "start_value":  100000.0,
            "start_date":   "2026-05-11",
            "total_pnl":    last["pnl_total"],
            "total_pnl_pct": last["pnl_total_pct"],
        }
        print(f"  Account from journal: ${last['equity']:,.0f}")
    else:
        account_summary = {
            "equity": 100000, "cash": 100000, "buying_power": 100000,
            "today_pnl": 0, "start_value": 100000,
            "start_date": "2026-05-11", "total_pnl": 0, "total_pnl_pct": 0,
        }

    # 4. Positions: prefer live, fallback to journal parse
    if not live_positions and history:
        # Try to get last known position from journal
        live_positions = []  # We'll show from journal context

    # 5. Assemble output
    out = {
        "last_updated": datetime.now().isoformat(timespec="seconds"),
        "account": account_summary,
        "positions": live_positions,
        "orders": orders[:20],
        "history": history,
        "journals": list(reversed(journals)),  # newest first
        "trade_decisions": trade_decisions,
        "strategy": {
            "name": "Beat the S&P 500",
            "max_position_pct": 5,
            "max_deployed_pct": 50,
            "stop_loss_pct": 7,
            "profit_target_pct": 15,
            "max_positions": 10,
            "daily_loss_limit_pct": 3,
        },
    }

    out_path = DOCS_DIR / "data.json"
    out_path.write_text(json.dumps(out, indent=2, default=str))
    print(f"  ✅ data.json written ({out_path.stat().st_size:,} bytes)")
    print("=== Dashboard data generated ===")

if __name__ == "__main__":
    main()
