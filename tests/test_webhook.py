import struct
from unittest.mock import patch

from mezon_helper_bot import webhook


def test_send_builds_image_payload(tmp_path):
    png = tmp_path / "a.png"
    png.write_bytes(
        b"\x89PNG\r\n\x1a\n" + b"\0\0\0\rIHDR" + struct.pack(">II", 1000, 500) + b"x"
    )
    with patch("mezon_helper_bot.webhook.requests.post") as post:
        webhook.send("https://hook", "hi", png, "https://img/a.png")
    msg = post.call_args.kwargs["json"]["message"]
    assert msg["t"] == "hi"
    assert (msg["images"][0]["w"], msg["images"][0]["h"]) == (1000, 500)
    assert msg["images"][0]["url"] == "https://img/a.png"
