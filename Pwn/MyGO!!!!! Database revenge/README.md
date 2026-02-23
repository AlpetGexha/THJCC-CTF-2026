# MyGO!!!!! Database revenge

**Point: 415**

nc chal.thjcc.org 10021

## Source-level vulnerability

```c
if (atoi(buf) != token) {
  printf(buf);
  puts("is not correct token!");
  try++;
  continue;
}
```

Two key points:

1. `atoi(buf)` is the auth check.
2. `printf(buf)` is a format-string vulnerability (user-controlled format string).

## 3. Initial primitives from format string

Using `%p` probing on remote, stack argument mapping was recovered:

- `%8$...` reads bytes `0..7` of `buf`
- `%9$...` reads bytes `8..15`
- `%10$...` reads bytes `16..23`

So we can inject an arbitrary pointer at bytes `16..23` and use `%10$...` to read/write it.

Example write primitive:

- `payload = b"%10$n" + b"A"*11 + p64(token_addr)`
- This writes `0` to `token`.

Then sending non-numeric input (`abc`) passes auth because `atoi("abc") == 0`.

## 4. Why login alone is not enough

After bypassing token check, service only prints database rows (no flag in normal output), so we need code execution.

## 5. Stack and libc reconstruction

From stack leaks:

- A stable libc leak (`%15$p`) gave `0x7ffff7db9d90`.
- Using provided libc offsets:
  - `atoi` offset `0x43640`
  - `system` offset `0x50d70`
- This established libc base used by service:
  - `0x7ffff7d90000`

From stack-memory reads (`%10$.8s` with arbitrary pointer):

- Return-chain slot around `0x7fffffffec68` is writable.
- `%10$hn` writes can patch 16-bit chunks of that chain.

## 6. Constraint: only 10 tries per `main`

A full chain needed more writes than one 10-try window, so exploitation was split into two stages:

### Stage 1 (first `main`)

- Overwrite return target to `__libc_start_call_main+0x16` low half (re-enters `main`, giving fresh 10 tries).
- Preload part of final chain (`pop rdi` and `system` words) in adjacent stack slots.

### Stage 2 (second `main`)

- Patch remaining words:
  - leading `ret` gadget (alignment),
  - `/bin/sh` pointer.
- Exhaust tries to trigger return and execute chain:
  - `ret -> pop rdi -> "/bin/sh" -> system`

Then send:

```sh
cat /flag.txt
```

## 7. Flag

`THJCC{54k1-ch4n_54k1-ch4n_54k1-ch4n_54k1-ch4n_54k1-ch4n_54k1-ch4n_54k1-ch4n_54k1-ch4n!!!!!!}`
