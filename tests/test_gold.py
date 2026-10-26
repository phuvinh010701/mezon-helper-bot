from datetime import datetime

from mezon_helper_bot.bots.gold import caption, render

ROWS = [("2026-10-25", 138.7, 141.7), ("2026-10-26", 138.7, 142.7)]


def test_caption_shows_change():
    text = caption([("Nhẫn", ROWS), ("Miếng", ROWS)], datetime(2026, 10, 26))
    assert "26/10/2026" in text and text.count("+1.0") == 2


def test_render_writes_png(tmp_path):
    out = tmp_path / "x" / "chart.png"
    render([("A", ROWS), ("B", ROWS)], out)
    assert out.read_bytes().startswith(b"\x89PNG")
