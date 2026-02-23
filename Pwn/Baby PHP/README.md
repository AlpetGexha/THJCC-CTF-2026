# Baby PHP

**Point: 463**

This is a baby web challenge.
:>

Note: ASLR is 0

http://chal-gcp.thjcc.org:60000/

## Source Analysis

### 1) `index.php`

```php
if (isset($_GET['f'])){
    echo file_get_contents('/app/'.$_GET['f']);
}

if (isset($_GET['txt'])){
    ...
    $res = whale_encrypt($_GET['txt']);
    ...
}
```

Two attack surfaces:

- `f`: file read with user-controlled path appended to `/app/` (traversal with `../../`)
- `txt`: passed to native extension function `whale_encrypt`

### 2) Extension (`whalecrypt.so`)

Reverse engineering `zif_whale_encrypt` shows unbounded copy of user input into a stack buffer (classic overflow), with saved return pointer controllable.

Important offsets used:

- RIP overwrite at `0xb8` from start of `txt` buffer
- Bytes `0x40..0x47` map to an internal length variable (`[rbp-0x70]`), set to `0` to stabilize path after overflow

---

## Exploit Strategy

### Phase A: Easy win checks

Try direct:

`/?f=../../getflag`

In this instance, that did not directly return a usable flag.

### Phase B: Build reliable ROP from leaked runtime

1. Leak maps:
   - `/?f=../../proc/self/maps`
2. Parse:
   - `whalecrypt.so` base
   - libc base + libc path
3. Leak remote libc bytes:
   - Example: `/?f=../../usr/lib/x86_64-linux-gnu/libc.so.6`
4. Resolve from leaked libc:
   - `system`
   - `exit`
   - `pop rdi ; ret`
   - write gadget: `mov [base+disp], src ; ... ; ret`
   - matching `pop <base>` / `pop <src>`

### Phase C: Command execution + exfil

Write command string into writable memory (`whale_base + 0x40f0`):

- `"/g*>x\0"`  
  (`/g*` expands to `/getflag`, output redirected to file `x` under `/app`)

ROP then calls:

1. writer gadget sequence to place command in memory
2. `system(cmd_ptr)`
3. `exit(0)` for cleaner end

The connection can still close abruptly; that is okay.  
After sending payload, read:

- `/?f=x`

and extract `THJCC{...}`.

---

## Solver Script

Implemented in:

- `exploit.py`

What it does:

1. Validates traversal surface (`?f=index.php`)
2. Tries direct `?f=../../getflag`
3. Leaks maps/libc
4. Auto-selects compatible libc write gadget + pops
5. Sends overflow payload via `?txt=<urlencoded-bytes>`
6. Reads dropped file `?f=x`
7. Extracts and prints flag

---

## Reproduce

```bash
python exploit.py --url http://chal-gcp.thjcc.org:60039/ --timeout 12 --attempts 5 --verbose
```

Expected success output includes:

```text
[+] Exploit succeeded via dropped file '/app/x'.
FLAG: THJCC{well_done_u_have_built_your_first_php_rop_chain_owob}
```

---
