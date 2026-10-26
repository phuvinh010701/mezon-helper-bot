"""CLI: python -m mezon_helper_bot <bot> [--dry-run]

The target channel comes from the WEBHOOK_URL env var, so each bot's workflow
decides where it posts.
"""

import argparse
import os

from mezon_helper_bot import webhook
from mezon_helper_bot.bots import BOTS
from mezon_helper_bot.hosting import publish_image


def main() -> None:
    parser = argparse.ArgumentParser(prog="mezon_helper_bot")
    parser.add_argument("bot", choices=sorted(BOTS))
    parser.add_argument(
        "--dry-run", action="store_true", help="build the post, don't publish or send"
    )
    args = parser.parse_args()

    post = BOTS[args.bot]()
    print(post.text)
    if args.dry_run:
        print(f"image: {post.image}")
        return

    image_url = publish_image(post.image) if post.image else None
    webhook.send(os.environ["WEBHOOK_URL"], post.text, post.image, image_url)


if __name__ == "__main__":
    main()
