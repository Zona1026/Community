from __future__ import annotations

import argparse
import json
import sys

from app import load_local_env
from db import run_scheduled_ingestion


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run one manual scheduled ingestion job.",
    )
    parser.add_argument(
        "--source",
        choices=["rss", "podcast"],
        required=True,
        help="Whitelisted ingestion source type.",
    )
    parser.add_argument(
        "--feed",
        required=True,
        help="Whitelisted feed key, such as hacker-news or planet-money.",
    )
    parser.add_argument(
        "--limit",
        default=5,
        type=int,
        help="Maximum items to process. Current MVP caps this at 5.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Build payloads and record the run without writing topics.",
    )

    return parser.parse_args()


def main() -> int:
    load_local_env()
    args = parse_args()
    result = run_scheduled_ingestion(
        source_type=args.source,
        source_key=args.feed,
        limit=args.limit,
        dry_run=args.dry_run,
    )

    print(json.dumps(result, ensure_ascii=True, indent=2))

    return 0 if result.get("status") == "success" else 1


if __name__ == "__main__":
    sys.exit(main())
