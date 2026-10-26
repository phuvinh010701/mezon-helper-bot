# mezon-helper-bot

Scheduled Mezon bots, run by GitHub Actions. Each bot is a function returning a `Post` (text + optional image) and posts to its own channel via a webhook.

## Setup
Per channel: create a webhook (channel → Edit Channel → Integrations → New Webhook), then add its URL as repo secret `<BOT>_WEBHOOK_URL`, e.g. `GOLD_WEBHOOK_URL`. The URL contains the token, so keep it a secret.

## Run locally
```bash
uv run python -m mezon_helper_bot gold --dry-run
```

## Add a bot
1. `src/mezon_helper_bot/bots/<name>.py` with `def run() -> Post`.
2. Register it in `bots/__init__.py`.
3. Copy `.github/workflows/gold.yml` → `<name>.yml`, change the cron and `bot:`.
4. Add repo secret `<NAME>_WEBHOOK_URL`.
