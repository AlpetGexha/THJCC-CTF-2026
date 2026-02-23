import argparse
import time
from dataclasses import dataclass, field

import numpy as np
import requests


@dataclass
class Oracle:
    url: str
    token: str
    timeout: float = 12.0
    remaining: int | None = None
    session: requests.Session = field(default_factory=requests.Session)

    def _post_json(self, path: str, payload: dict, allow_400: bool = False) -> dict:
        headers = {"Authorization": f"Bearer {self.token}"}
        delay = 0.2
        last_exc: Exception | None = None

        for _ in range(8):
            try:
                r = self.session.post(
                    f"{self.url.rstrip('/')}{path}",
                    json=payload,
                    headers=headers,
                    timeout=self.timeout,
                )
                if r.status_code >= 500:
                    raise requests.HTTPError(f"server {r.status_code}", response=r)
                if r.status_code == 400 and allow_400:
                    return r.json()
                r.raise_for_status()
                return r.json()
            except (requests.Timeout, requests.ConnectionError, requests.HTTPError) as e:
                last_exc = e
                time.sleep(delay)
                delay = min(delay * 1.8, 2.0)

        raise RuntimeError(f"request failed after retries: {path}: {last_exc}")

    def predict_once(self, x: np.ndarray) -> int:
        data = self._post_json("/predict", {"x": x.tolist()})
        self.remaining = data.get("remaining", self.remaining)
        return int(data["label"])

    def predict_vote(self, x: np.ndarray, reps: int = 3) -> int:
        ones = 0
        for _ in range(reps):
            ones += self.predict_once(x)
        return 1 if ones * 2 >= reps else 0

    def submit(self, n_guess: np.ndarray, beta_guess: float) -> dict:
        return self._post_json(
            "/submit",
            {"n_guess": n_guess.tolist(), "beta_guess": float(beta_guess)},
            allow_400=True,
        )


def register(url: str, timeout: float = 12.0) -> tuple[str, int]:
    delay = 0.2
    last_exc: Exception | None = None
    with requests.Session() as s:
        for _ in range(8):
            try:
                r = s.post(f"{url.rstrip('/')}/register", timeout=timeout)
                if r.status_code >= 500:
                    raise requests.HTTPError(f"server {r.status_code}", response=r)
                r.raise_for_status()
                data = r.json()
                return data["player_token"], int(data["query_limit"])
            except (requests.Timeout, requests.ConnectionError, requests.HTTPError) as e:
                last_exc = e
                time.sleep(delay)
                delay = min(delay * 1.8, 2.0)
    raise RuntimeError(f"register failed after retries: {last_exc}")


def random_unit(dim: int, rng: np.random.Generator) -> np.ndarray:
    v = rng.normal(size=dim)
    n = np.linalg.norm(v)
    if n == 0:
        return random_unit(dim, rng)
    return v / n


def find_boundary_point(
    oracle: Oracle,
    u: np.ndarray,
    reps_search: int,
    reps_check: int,
    bsteps: int,
    start_r: float,
    max_expand: int,
) -> np.ndarray | None:
    r = start_r

    y_lo = oracle.predict_vote(-r * u, reps=reps_search)
    y_hi = oracle.predict_vote(r * u, reps=reps_search)

    expands = 0
    while y_lo == y_hi and expands < max_expand:
        r *= 2.0
        y_lo = oracle.predict_vote(-r * u, reps=reps_search)
        y_hi = oracle.predict_vote(r * u, reps=reps_search)
        expands += 1

    if y_lo == y_hi:
        return None

    lo, hi = -r, r
    for _ in range(bsteps):
        mid = 0.5 * (lo + hi)
        y_mid = oracle.predict_vote(mid * u, reps=reps_search)
        if y_mid == y_lo:
            lo = mid
            y_lo = y_mid
        else:
            hi = mid
            y_hi = y_mid

    t = 0.5 * (lo + hi)

    # Check that labels differ on a small neighborhood around estimated boundary.
    eps = max(1e-4, 2.0 * (hi - lo))
    y_l = oracle.predict_vote((t - eps) * u, reps=reps_check)
    y_r = oracle.predict_vote((t + eps) * u, reps=reps_check)
    if y_l == y_r:
        return None

    return t * u


def fit_plane(points: np.ndarray) -> tuple[np.ndarray, float]:
    p = points.copy()

    n_hat = None
    beta_hat = None
    for _ in range(6):
        a = np.hstack([p, np.ones((p.shape[0], 1))])
        _, _, vt = np.linalg.svd(a, full_matrices=False)
        v = vt[-1]
        n = v[:-1]
        beta = float(v[-1])

        norm = np.linalg.norm(n)
        if norm == 0:
            break
        n = n / norm
        beta = beta / norm

        n_hat, beta_hat = n, beta

        resid = np.abs(p @ n_hat + beta_hat)
        med = float(np.median(resid))
        thresh = max(1e-4, 3.0 * med)
        keep = resid <= thresh
        if np.count_nonzero(keep) < max(20, p.shape[1] + 2):
            break
        p = p[keep]

    if n_hat is None:
        raise RuntimeError("failed to fit hyperplane")

    return n_hat, beta_hat


def beta_from_distance_oracle(oracle: Oracle, n_guess: np.ndarray) -> float:
    # Use /submit beta_error leak to recover beta exactly (up to float precision).
    r0 = oracle.submit(n_guess, 0.0)
    if r0.get("ok") is True:
        return 0.0
    d0 = float(r0["beta_error"])

    r1 = oracle.submit(n_guess, 1.0)
    if r1.get("ok") is True:
        return 1.0
    d1 = float(r1["beta_error"])

    cands = [-d0, d0]
    beta = min(cands, key=lambda c: abs(abs(c - 1.0) - d1))
    return float(beta)


def solve_one(
    url: str,
    dim: int,
    points_target: int,
    reps_search: int,
    reps_check: int,
    bsteps: int,
    seed: int,
) -> tuple[bool, dict]:
    token, qlim = register(url)
    oracle = Oracle(url=url, token=token)
    rng = np.random.default_rng(seed)

    print(f"[+] token={token} query_limit={qlim}")

    pts: list[np.ndarray] = []
    tries = 0
    while len(pts) < points_target:
        tries += 1
        if oracle.remaining is not None and oracle.remaining < 350:
            print("[-] low remaining query budget; stopping collection")
            break

        u = random_unit(dim, rng)
        p = find_boundary_point(
            oracle,
            u,
            reps_search=reps_search,
            reps_check=reps_check,
            bsteps=bsteps,
            start_r=1.0,
            max_expand=18,
        )
        if p is None:
            continue

        pts.append(p)
        if len(pts) % 5 == 0:
            rem = oracle.remaining if oracle.remaining is not None else -1
            print(f"    collected {len(pts)}/{points_target} points (tries={tries}, remaining={rem})")

    if len(pts) < dim + 4:
        return False, {"error": "not enough boundary points", "token": token}

    points = np.vstack(pts)
    n_hat, beta_hat = fit_plane(points)

    # Fix orientation with robust vote at origin.
    y0 = oracle.predict_vote(np.zeros(dim), reps=11)
    if (1 if beta_hat >= 0 else 0) != y0:
        n_hat = -n_hat
        beta_hat = -beta_hat

    # Recover beta precisely from submit leak.
    beta_hat = beta_from_distance_oracle(oracle, n_hat)

    sub = oracle.submit(n_hat, beta_hat)
    print("[+] submit response:", sub)
    if sub.get("ok"):
        return True, {"token": token, "response": sub, "n": n_hat, "beta": beta_hat}

    # Try sign flip if needed.
    sub_flip = oracle.submit(-n_hat, -beta_hat)
    if sub_flip.get("ok"):
        return True, {"token": token, "response": sub_flip, "n": -n_hat, "beta": -beta_hat}

    # Keep the better of two by max_error if available.
    best = sub
    if isinstance(sub, dict) and isinstance(sub_flip, dict):
        me = sub.get("max_error", float("inf"))
        me2 = sub_flip.get("max_error", float("inf"))
        if me2 < me:
            best = sub_flip

    return False, {
        "token": token,
        "response": best,
        "n": n_hat,
        "beta": beta_hat,
        "remaining": oracle.remaining,
    }


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Steal My Model solver")
    p.add_argument("--url", default="http://chal.thjcc.org:31443")
    p.add_argument("--dim", type=int, default=16)
    p.add_argument("--attempts", type=int, default=5)
    p.add_argument("--points", type=int, default=44)
    p.add_argument("--reps-search", type=int, default=3)
    p.add_argument("--reps-check", type=int, default=5)
    p.add_argument("--bsteps", type=int, default=30)
    p.add_argument("--seed", type=int, default=int(time.time()))
    return p.parse_args()


def main() -> None:
    args = parse_args()

    for k in range(args.attempts):
        print(f"\n=== attempt {k + 1}/{args.attempts} ===")
        ok, info = solve_one(
            url=args.url,
            dim=args.dim,
            points_target=args.points,
            reps_search=args.reps_search,
            reps_check=args.reps_check,
            bsteps=args.bsteps,
            seed=args.seed + 1009 * k,
        )
        if ok:
            print("\n[FLAG]", info["response"])
            return

        print("[-] attempt failed")
        print(info.get("response", info))

    raise SystemExit("all attempts failed")


if __name__ == "__main__":
    main()
