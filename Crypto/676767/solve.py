import socket
import re
import time

HOST = 'chal.thjcc.org'
PORT = 48764
BASE = 86844066927987146567678238756515930889952488499230423029593188005934867676767


def recv_until(sock, marker: bytes, timeout=5.0):
    sock.settimeout(timeout)
    data = b''
    while marker not in data:
        chunk = sock.recv(4096)
        if not chunk:
            break
        data += chunk
    return data


def attempt(i):
    s = socket.create_connection((HOST, PORT), timeout=5)
    data = recv_until(s, b'a>')
    text = data.decode(errors='ignore')
    nums = [int(x) for x in re.findall(r'<\s*(\d+)', text)]
    if len(nums) != 10:
        s.close()
        return False, f'attempt {i}: failed to parse 10 leaks, got {len(nums)}\n{text}'

    if not all(x < BASE for x in nums):
        s.close()
        return False, f'attempt {i}: skip (not all leaks < base)'

    s.sendall(b'-1\n')
    recv_until(s, b'b>')
    s.sendall(b'0\n')

    for n in nums:
        recv_until(s, b'> ')
        s.sendall(f"{n}\n".encode())

    tail = s.recv(4096)
    s.close()
    out = tail.decode(errors='ignore')
    if 'THJCC{' in out:
        return True, out.strip()
    return False, f'attempt {i}: submitted but no flag: {out!r}'


def main():
    for i in range(1, 400):
        try:
            ok, msg = attempt(i)
            print(msg)
            if ok:
                return
        except Exception as e:
            print(f'attempt {i}: error: {e}')
        time.sleep(0.08)


if __name__ == '__main__':
    main()
