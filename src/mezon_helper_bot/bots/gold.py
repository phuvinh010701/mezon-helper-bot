"""Daily SJC gold price chart (data: vang.today)."""

from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import matplotlib
import requests

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from mezon_helper_bot.base import Post

API = "https://www.vang.today/api/prices"
CODE = "SJL1L10"  # SJC 9999
DAYS = 30
OUT_DIR = Path("assets/gold")

Row = tuple[str, float, float]  # (date, buy, sell) in million VND / tael


def fetch_history() -> list[Row]:
    resp = requests.get(API, params={"type": CODE, "days": DAYS}, timeout=30)
    resp.raise_for_status()
    history = sorted(resp.json()["history"], key=lambda h: h["date"])
    return [
        (h["date"], h["prices"][CODE]["buy"] / 1e6, h["prices"][CODE]["sell"] / 1e6)
        for h in history
    ]


def render(rows: list[Row], path: Path) -> None:
    days = [r[0][5:] for r in rows]
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(days, [r[2] for r in rows], label="Bán", color="#d62728", marker="o", ms=3)
    ax.plot(days, [r[1] for r in rows], label="Mua", color="#1f77b4", marker="o", ms=3)
    ax.set_title(f"Giá vàng SJC 9999 - {len(rows)} ngày (triệu đồng/lượng)")
    ax.set_xticks(days[:: max(1, len(days) // 10)])
    ax.grid(alpha=0.3)
    ax.legend()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=110, bbox_inches="tight")
    plt.close(fig)


def caption(rows: list[Row], today: datetime) -> str:
    _, buy, sell = rows[-1]
    change = sell - rows[-2][2] if len(rows) > 1 else 0.0
    return (
        f"Vàng SJC {today:%d/%m/%Y}: mua {buy:.1f}tr / bán {sell:.1f}tr "
        f"({change:+.1f}tr so với hôm qua)"
    )


def run() -> Post:
    today = datetime.now(ZoneInfo("Asia/Ho_Chi_Minh"))
    rows = fetch_history()
    image = OUT_DIR / f"{today:%Y-%m-%d}.png"
    render(rows, image)
    return Post(text=caption(rows, today), image=image)
