# Lock?

**Point: 498**

### Description

My friend locked his personal webpage for some reason, but did he really?

**Target:** `thjcc.tcp.tw`

**Hint:** Try clicking on anything clickable on the Google login page. By the way, it's an OSINT challenge.

---

### Solution

This was an OSINT (Open Source Intelligence) challenge involving following a trail of digital footprints:

1.  **GitHub Discovery**: Checking the GitHub profile for `418meow` revealed a 'special' repository. Redirects from the username `m41657557` confirmed it was a previous alias for the same user.
2.  **Metadata Leak**: Analyzing GitHub metadata revealed the email `jaylen0721@tcp.tw`.
3.  **Social Media Pivot**: Searching for the handle `jaylen0721` led to a Twitter account that mentioned `hackmd.io` as being "useful."
4.  **HackMD Investigation**: On HackMD, the user `jaylen0721` was found following only one other user: `wilson2026`.
5.  **Finding the Blog**: The HackMD profile for `wilson2026` linked to a personal blog.
6.  **Web Archiving**: The blog itself appeared to be locked or changed, but checking the **Wayback Machine** (Web Archive) revealed a snapshot from February 14, 2026:
    `https://web.archive.org/web/20260214130957/https://m2k4b3jo8z.pages.dev/`

This archived page contained the necessary information to bypass the lock.

## Flag

`THJCC{42vj6Dx}`
