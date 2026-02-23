import argparse
import sys

import requests


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--url", default="http://127.0.0.1:31443")
    p.add_argument("--run", action="store_true", help="actually request a token")
    if len(sys.argv) == 1:
        p.print_help()
        raise SystemExit(0)
    return p.parse_args()


def main() -> None:
    args = parse_args()
    if not args.run:
        print("Use --run to execute. Example:")
        print("  python get_token.py --run --url http://127.0.0.1:31443")
        return

    r = requests.post(f"{args.url.rstrip('/')}/register", timeout=5)
    r.raise_for_status()
    data = r.json()
    print("player_token:", data["player_token"])
    print("query_limit:", data["query_limit"])


if __name__ == "__main__":
    main()
