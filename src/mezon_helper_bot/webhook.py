"""Post a message (optionally with one image) to a Mezon channel webhook."""

import struct
from pathlib import Path

import requests


def _image_payload(path: Path, url: str) -> dict:
    data = path.read_bytes()
    width, height = struct.unpack(">II", data[16:24])  # PNG IHDR
    return {
        "fn": path.name,
        "sz": len(data),
        "ft": "image/png",
        "w": width,
        "h": height,
        "url": url,
    }


def send(
    webhook_url: str, text: str, image: Path | None = None, image_url: str | None = None
) -> None:
    message: dict = {"t": text}
    if image and image_url:
        message["images"] = [_image_payload(image, image_url)]
    resp = requests.post(
        webhook_url, json={"type": "hook", "message": message}, timeout=30
    )
    resp.raise_for_status()
