"""Daily gold price chart: PNJ plain ring + SJC bar (data: vang.today)."""

from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import matplotlib
import requests

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.figure import SubFigure

from mezon_helper_bot.base import Post

API = "https://www.vang.today/api/prices"
# (vang.today code, card title, short name for the caption)
PRODUCTS = [
    ("PQHN24NTT", "NHẪN TRƠN PNJ 9999", "Nhẫn trơn PNJ 9999"),
    ("SJL1L10", "VÀNG MIẾNG SJC 9999", "Vàng miếng SJC"),
]
DAYS = 30
OUT_DIR = Path("assets/gold")

Row = tuple[str, float, float]  # (date, buy, sell) in million VND / tael
Card = tuple[str, list[Row]]  # (title, rows)


def fetch_history(code: str) -> list[Row]:
    resp = requests.get(API, params={"type": code, "days": DAYS}, timeout=30)
    resp.raise_for_status()
    history = sorted(resp.json()["history"], key=lambda h: h["date"])
    return [
        (h["date"], h["prices"][code]["buy"] / 1e6, h["prices"][code]["sell"] / 1e6)
        for h in history
    ]


# Dark card palette: the PNG carries its own background so it reads in any Mezon theme.
BG, TEXT, MUTED, GRID = "#0f172a", "#f1f5f9", "#94a3b8", "#243049"
SELL, BUY = "#fbbf24", "#7dd3fc"
UP, DOWN = "#34d399", "#f87171"


def _label(date: str) -> str:
    return f"{date[8:]}/{date[5:7]}"


def draw_card(fig: SubFigure, title: str, rows: list[Row]) -> None:
    n = len(rows)
    sell = [r[2] for r in rows]
    buy = [r[1] for r in rows]
    xs = range(n)
    change = sell[-1] - sell[-2] if n > 1 else 0.0
    arrow, color = (
        ("▲", UP) if change > 0 else ("▼", DOWN) if change < 0 else ("–", MUTED)
    )

    def text(x: float, y: float, s: str, size: int, color: str = TEXT, **kw) -> None:
        fig.text(x, y, s, fontsize=size, color=color, **kw)

    # Header: hero number on the left, secondary stats on the right.
    text(0.06, 0.915, f"GIÁ {title}", 11, MUTED, fontweight="bold")
    text(0.06, 0.805, f"{sell[-1]:.1f}", 34, SELL, fontweight="bold")
    text(
        0.06 + 0.0175 * len(f"{sell[-1]:.1f}") * 2.2,
        0.815,
        "triệu đồng / lượng (bán ra)",
        11,
        MUTED,
    )
    text(
        0.06,
        0.745,
        f"{arrow} {change:+.1f} tr so với hôm qua",
        11,
        color,
        fontweight="bold",
    )
    for i, (k, v) in enumerate(
        [
            ("Mua vào", f"{buy[-1]:.1f}"),
            ("Chênh lệch", f"{sell[-1] - buy[-1]:.1f}"),
            (f"Cao nhất {n}n", f"{max(sell):.1f}"),
        ]
    ):
        text(0.94, 0.915 - i * 0.065, f"{k}   ", 10, MUTED, ha="right")
        text(0.94, 0.915 - i * 0.065, v, 10, TEXT, ha="left", fontweight="bold")

    ax = fig.add_axes((0.06, 0.09, 0.80, 0.60), facecolor=BG)
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.grid(axis="y", color=GRID, linewidth=1)
    ax.set_axisbelow(True)
    ax.tick_params(colors=MUTED, labelsize=9, length=0)

    ax.fill_between(xs, buy, sell, color=SELL, alpha=0.12, linewidth=0)
    ax.plot(xs, buy, color=BUY, linewidth=2, label="Mua", solid_capstyle="round")
    ax.plot(xs, sell, color=SELL, linewidth=2.5, label="Bán", solid_capstyle="round")
    for series, c in ((buy, BUY), (sell, SELL)):
        ax.scatter(
            [n - 1], [series[-1]], s=70, color=c, edgecolor=BG, linewidth=2, zorder=5
        )
        ax.annotate(
            f"{series[-1]:.1f}",
            (n - 1, series[-1]),
            xytext=(10, 0),
            textcoords="offset points",
            color=TEXT,
            fontsize=10,
            fontweight="bold",
            va="center",
            annotation_clip=False,
        )

    hi = max(range(n), key=sell.__getitem__)
    if 0 < hi < n - 1:
        ax.annotate(
            f"Cao nhất {sell[hi]:.1f}",
            (hi, sell[hi]),
            xytext=(0, 10),
            textcoords="offset points",
            color=MUTED,
            fontsize=9,
            ha="center",
        )

    pad = (max(sell) - min(buy)) * 0.12
    ax.set_ylim(min(buy) - pad, max(sell) + pad)
    ax.set_xlim(-0.5, n - 0.5)
    step = max(1, n // 6)
    ticks = range(n - 1, -1, -step)  # always ends on today
    ax.set_xticks(list(ticks), [_label(rows[i][0]) for i in ticks])
    ax.legend(loc="upper left", frameon=False, labelcolor=MUTED, fontsize=9, ncol=2)


def render(cards: list[Card], path: Path) -> None:
    fig = plt.figure(figsize=(10, 5.8 * len(cards)), facecolor=BG)
    for sub, (title, rows) in zip(fig.subfigures(len(cards), 1, hspace=0), cards):
        draw_card(sub, title, rows)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=120, facecolor=BG)
    plt.close(fig)


def caption(cards: list[tuple[str, list[Row]]], today: datetime) -> str:
    lines = [f"Giá vàng {today:%d/%m/%Y} (triệu đồng/lượng)"]
    for name, rows in cards:
        _, buy, sell = rows[-1]
        change = sell - rows[-2][2] if len(rows) > 1 else 0.0
        lines.append(
            f"• {name}: mua {buy:.1f} / bán {sell:.1f} ({change:+.1f} so với hôm qua)"
        )
    return "\n".join(lines)


def run() -> Post:
    today = datetime.now(ZoneInfo("Asia/Ho_Chi_Minh"))
    data = {code: fetch_history(code) for code, _, _ in PRODUCTS}
    image = OUT_DIR / f"{today:%Y-%m-%d}.png"
    render([(title, data[code]) for code, title, _ in PRODUCTS], image)
    return Post(
        text=caption([(name, data[code]) for code, _, name in PRODUCTS], today),
        image=image,
    )
