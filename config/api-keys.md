# API Keys — Status Checklist

> Actual keys are stored in `~/.openclaw/workspace/alpaca_config.json` and `~/.openclaw/workspace/perplexity_config.json`
> NEVER store raw API keys in this file.

## Keys Required

| Key | Status | Stored At |
|-----|--------|-----------|
| Alpaca API Key (paper) | ✅ CONFIGURED | alpaca_config.json |
| Alpaca Secret Key (paper) | ✅ CONFIGURED | alpaca_config.json |
| Alpaca Base URL | ✅ paper-api.alpaca.markets/v2 | alpaca_config.json |
| Perplexity API Key | ✅ CONFIGURED | perplexity_config.json |

## Environment Variables Needed in Claude Code
When setting up Claude Code cloud routines, these env vars must be added:
- `ALPACA_API_KEY`
- `ALPACA_SECRET_KEY`
- `ALPACA_BASE_URL`
- `PERPLEXITY_API_KEY`
