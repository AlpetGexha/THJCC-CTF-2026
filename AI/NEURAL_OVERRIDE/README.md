# NEURAL_OVERRIDE

**Point: 264**

AI is not always as safe as it seems. Can you find the vulnerability hidden within this model?

## Description Summary

The site asks us to upload a custom `.pt` tensor that:

- stays within `L2_DIST < 0.05` from the original tensor
- forces prediction to `CLASS_ID_3`
- with `confidence >= 90%`

At first this looks like an adversarial example optimization problem, but the real issue is unsafe deserialization.

## Recon

The page exposes:

- `GET /download_origin` -> original tensor (`origin.pt`)
- `POST /judge` -> checks uploaded `.pt`

Uploading invalid files (for example plain text) returns raw deserialization errors.  
This strongly indicates the server is doing `torch.load()` on user-controlled input.

## Vulnerability

`torch.load` uses Python pickle (unless hardened). Pickle is code-execution capable.

If the server loads arbitrary `.pt` from users with unsafe settings, we can execute code during deserialization (`__reduce__` gadget).

That means we can:

1. monkeypatch runtime functions used in validation (`torch.norm`, `torch.dist`)
2. monkeypatch softmax output to force class 3 with high confidence
3. return a valid tensor object so the judge flow continues

## Exploit Strategy

Inside payload `__reduce__`, execute Python code that:

- sets `torch.norm` and/or `torch.dist` to always return `0.0`
- sets `torch.softmax` and `torch.nn.functional.softmax` to return a fixed probability vector with class index `3` at `1.0`
- returns `torch.zeros((1,3,32,32))` as a valid tensor

This bypasses all checks without needing true adversarial optimization.

## Flag

`THJCC{y0ur_ar3_the_adv3rs3r1al_attack_m0st3r}`
