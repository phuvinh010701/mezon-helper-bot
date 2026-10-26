"""Bot registry: add a module in this package, then list it here."""

from mezon_helper_bot.base import Bot
from mezon_helper_bot.bots import gold

BOTS: dict[str, Bot] = {
    "gold": gold.run,
}
