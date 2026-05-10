"""
Shared utilities for the trading agent.
"""
import json
import os
import subprocess
from datetime import datetime, date
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).parent.parent
MEMORY_DIR = BASE_DIR / "memory"
JOURNAL_DIR = BASE_DIR / "journal"
LOGS_DIR = BASE_DIR / "logs"

JOURNAL_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

# Load API configs
def load_config():
    workspace = Path.home() / ".openclaw" / "workspace"
    alpaca = json.loads((workspace / "alpaca_config.json").read_text())
    perplexity = json.loads((workspace / "perplexity_config.json").read_text())
    return alpaca, perplexity

# Alpaca client
def get_alpaca_client():
    from alpaca.trading.client import TradingClient
    alpaca_cfg, _ = load_config()
    return TradingClient(
        api_key=alpaca_cfg["api_key"],
        secret_key=alpaca_cfg["secret_key"],
        paper=True
    )

# Portfolio state
def load_portfolio():
    path = MEMORY_DIR / "portfolio.json"
    return json.loads(path.read_text())

def save_portfolio(data):
    path = MEMORY_DIR / "portfolio.json"
    data["last_updated"] = datetime.now().isoformat()
    path.write_text(json.dumps(data, indent=2))

def load_watchlist():
    path = MEMORY_DIR / "watchlist.json"
    try:
        return json.loads(path.read_text())
    except:
        return {"stocks": [], "last_updated": None}

def save_watchlist(data):
    path = MEMORY_DIR / "watchlist.json"
    data["last_updated"] = datetime.now().isoformat()
    path.write_text(json.dumps(data, indent=2))

# Journal
def today_journal_path():
    return JOURNAL_DIR / f"{date.today().isoformat()}.md"

def append_journal(text):
    path = today_journal_path()
    timestamp = datetime.now().strftime("%H:%M AEST")
    with open(path, "a") as f:
        f.write(f"\n## {timestamp}\n{text}\n")
    log(f"Journal updated: {path}")

def log(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {msg}")
    log_path = LOGS_DIR / f"{date.today().isoformat()}.log"
    with open(log_path, "a") as f:
        f.write(f"[{timestamp}] {msg}\n")

# Ask Claude for a decision
def ask_claude(prompt, max_tokens=2000):
    """Run claude -p with a prompt and return the response."""
    result = subprocess.run(
        ["claude", "-p", prompt, "--model", "claude-sonnet-4-6"],
        capture_output=True, text=True, timeout=120
    )
    if result.returncode != 0:
        log(f"Claude error: {result.stderr}")
        return None
    return result.stdout.strip()

# Perplexity research
def perplexity_search(query):
    import requests
    _, perp_cfg = load_config()
    headers = {
        "Authorization": f"Bearer {perp_cfg['api_key']}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": perp_cfg.get("pro_model", "sonar-pro"),
        "messages": [{"role": "user", "content": query}],
        "max_tokens": 1000
    }
    resp = requests.post(
        "https://api.perplexity.ai/chat/completions",
        json=payload, headers=headers, timeout=30
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]

# Check guardrails
def check_guardrails(portfolio):
    """Returns (ok, reason). If not ok, halt trading."""
    if portfolio.get("emergency_stop"):
        return False, "EMERGENCY STOP active"
    if portfolio.get("trading_paused"):
        return False, "Trading paused (daily loss limit hit)"
    
    equity = portfolio.get("total_equity", 100000)
    start = portfolio.get("start_equity", 100000)
    todays_pnl = portfolio.get("todays_pnl", 0)
    
    # Emergency stop: -15% from start
    if equity < start * 0.85:
        portfolio["emergency_stop"] = True
        save_portfolio(portfolio)
        return False, f"EMERGENCY STOP: Portfolio at ${equity:,.0f} (-15% from start)"
    
    # Daily loss limit: -3%
    if todays_pnl < -(start * 0.03):
        portfolio["trading_paused"] = True
        save_portfolio(portfolio)
        return False, f"Daily loss limit hit: ${todays_pnl:,.0f}"
    
    return True, "ok"
