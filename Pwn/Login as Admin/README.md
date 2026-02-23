# Login as Admin

**Point: 410**

I think I made a very secure login system, so no one can hack it

nc chal.thjcc.org 10003

## 1. Recon

Key observations:

1. `username` is read with `read(0, username, 0x100)` and is **not null-terminated**.
2. On failure, `printf("%s login failed!\n", username)` prints bytes past the buffer until it hits `\x00`.
3. `admin_password` is actually `&system`, so leaking nearby stack data can reveal a libc pointer.

## 2. Vulnerability

This is an information leak from an unterminated string:

- `username` fills exactly `0x100` bytes.
- `printf("%s", username)` keeps reading into adjacent stack variables.
- Adjacent data includes pointer-sized values from the stack frame (`password`, `admin_password`, saved data).
- A leaked libc-looking pointer lets us compute the needed password value.

## 3. Exploit Plan

Use two logins in one connection:

1. **Leak phase**
   - Send menu option `1`.
   - Send `A * 0x100` as username (no null byte).
   - Send any 8-byte password.
   - Parse the echoed failure line and extract leaked bytes after the 0x100 username bytes.
2. **Bypass phase**
   - Compute `system` from the leak (`system = leak - delta` used by this instance).
   - Send menu option `1` again.
   - Username: `admin\x00` (so `strcmp(username, "admin") == 0`).
   - Password: packed computed `system` pointer.
3. On success, service spawns `/bin/sh`; send `cat /flag.txt`.

## 4. Solver Script

`solve.py` automates:

1. Connect to `chal.thjcc.org:10003`.
2. Trigger a harmless invalid menu input once (stack grooming helper in script).
3. Leak a libc pointer from failed login output.
4. Compute `system` address.
5. Login as `admin` with that value as password.
6. Execute `cat /flag.txt; exit`.

Run:

```bash
python solve.py
```

## 5. Result

Recovered flag:

```text
THJCC{u3e_1nf0rm4t1on_l3ak_t0_g3t_l1bc_bas3_4nd_g3t_adm1n_p@ssw0rd_th3n_RCE!!!}
```

# Flag

`THJCC{u3e_1nf0rm4t1on_l3ak_t0_g3t_l1bc_bas3_4nd_g3t_adm1n_p@ssw0rd_th3n_RCE!!!}`
