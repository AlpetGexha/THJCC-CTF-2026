# msgboard

**Point: 356**

http://chal.thjcc.org:36001/

## Initial Recon

The port `36001` endpoint is an instance manager (not the vulnerable app itself).  
The actual challenge app is exposed on spawned ports and serves the Flask message board.

## Source Analysis Summary

The provided source contains multiple security issues:

1. Hidden-post content leak

- File: `thjccanon/api.py:94`
- Endpoint: `GET /api/v1/mb_replys/?post_id=...`
- Bug: even if a post is hidden, the API still returns raw post content:
  - `thjccanon/api.py:124` -> `"content": data["content"]`
- Impact: moderation-hidden data can still be read by direct API calls.

2. Unsafe upload filename handling (path traversal write)

- File: `thjccanon/api.py:251`
- Endpoint: `POST /api/v1/upload_image`
- Bug:
  - `secure_filename(filename)` is called but its result is not used for saving.
  - Save uses original filename directly:
    - `thjccanon/api.py:275` -> `file.save(os.path.join(app.config.get("UPLOAD_FOLDER", ""), filename))`
- Impact: attacker can attempt arbitrary file write via crafted filename/path segments.

3. Risky image proxy trust model

- Files:
  - `little_conponment.py:60`
  - `little_conponment.py:61`
  - `app.py:52`
  - `docker-compose.yml:13`
- Behavior: markdown images are rewritten through `IMAGE_PROXY_URL`, which can become an attack surface when URL validation/allowlisting is weak in deployment.

## Exploitation Process

1. Identify live app instances (not just the instancer page).
2. Query board API on live instances:
   - `GET /api/v1/mb_board/`
3. Extract suspicious content from posts.

One live instance returned a post containing an embedded flag marker in the content payload.

## Working Request

```bash
curl "http://chal.thjcc.org:35036/api/v1/mb_board/"
```

Response contained:

```text
THJCC{model2rce456ytrrghdrydhrth}
```

## Flag

`THJCC{model2rce456ytrrghdrydhrth}`
