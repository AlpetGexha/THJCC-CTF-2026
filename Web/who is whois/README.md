# who is whois

**Point: 100**

who is whois???

<http://chal.thjcc.org:13316/>

## Source Analysis

From `chal/app.py`:

1. `whois` route:

```python
raw = request.form.get("domain", "").strip()
args = ["whois"] + shlex.split(raw)
proc = subprocess.run(args, capture_output=True, text=True, timeout=15)
```

No shell is used, so `;`, `&&`, `|` won't work.  
But `shlex.split` lets us inject **arguments** into `whois`.

1. `flag` route:

```python
if request.remote_addr not in {"127.0.0.1", "::1"}: deny
if request.headers.get("admin", "") != "thjcc": deny
if not pyotp.TOTP(_get_totp_secret()).verify(safekey): deny
return FLAG_VALUE
```

1. TOTP secret recovery:

```python
_ENC_SECRET = "Jl5cLlcsI10sKCYhLS40IykpMyQnIF8wIjEtPTM6OzI="
_XOR_KEY = "thjcc"
```

`_get_totp_secret()` is Base64 decode then XOR with `thjcc`, giving:

`R66M4XK7OKRIGMWWACPGSH5SAEEWPYOZ`

## Exploit Strategy

1. Generate current TOTP from recovered secret.
2. Send to `/whois` a payload that injects whois options:
   - `-h 127.0.0.1 -p 13316`
3. Use a single-quoted multi-line query so whois sends raw HTTP text:
   - `POST /flag HTTP/1.1`
   - `admin: thjcc`
   - body `safekey=<totp>`
4. The request originates from localhost, so `/flag` returns the flag.

Expected output includes:

# Flag

`THJCC{yeyoumeng_Wh0i5_SsRf}`
