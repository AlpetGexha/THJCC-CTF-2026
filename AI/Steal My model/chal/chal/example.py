import argparse
import sys
from typing import List

import requests


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--url", default="http://127.0.0.1:31443")
    p.add_argument("--token", required=True)
    p.add_argument("--dim", type=int, default=16)
    p.add_argument(
        "--x",
        default=None,
        help='comma-separated vector, e.g. "0,0,1.5,-2". If omitted, uses all-zero vector.',
    )
    p.add_argument("--run", action="store_true", help="actually run the example workflow")
    if len(sys.argv) == 1:
        p.print_help()
        raise SystemExit(0)
    return p.parse_args()


def predict(url: str, token: str, x: List[float]) -> dict:
    r = requests.post(
        f"{url.rstrip('/')}/predict",
        json={"x": x},
        headers={"Authorization": f"Bearer {token}"},
        timeout=5,
    )
    r.raise_for_status()
    return r.json()


def parse_x(raw: str | None, dim: int) -> List[float]:
    if raw is None:
        return [0.0] * dim
    vals = [s.strip() for s in raw.split(",") if s.strip() != ""]
    if len(vals) != dim:
        raise SystemExit(f"--x must contain exactly {dim} numbers")
    try:
        return [float(v) for v in vals]
    except ValueError as e:
        raise SystemExit(f"invalid --x: {e}") from e


def main() -> None:
    args = parse_args()
    if not args.run:
        print("Use --run to execute. Example:")
        print(
            "  python example.py --run --url http://127.0.0.1:31443 "
            '--token <player_token> --dim 16 --x "0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0"'
        )
        return

    x = parse_x(args.x, args.dim)
    result = predict(args.url, args.token, x)
    print("request x:", x)
    print("response:", result)


if __name__ == "__main__":
    main()
