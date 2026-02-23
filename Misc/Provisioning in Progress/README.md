# Provisioning in Progress

**Point: 100**

### Description

AS201943 has recently begun deploying its production infrastructure. According to the NOC provisioning policy, Operational status is based on live network deployment. Address assignments alone do not imply production readiness.

Your task is to determine which infrastructure is actually in production and retrieve the NOC authorization token from the public registry (RIPE/WHOIS).

---

### Solution

#### 1. OSINT Reconnaissance

A WHOIS query for **AS201943** returns several IPv6 prefixes. By following the "Operational status" policy, we filter out "Lab" or "Pending" blocks and focus on the **ACTIVE** core infrastructure.

- **Active Prefix:** `2a14:7581:6fa0::/48`
- **Description:** `CORE INFRASTRUCTURE (ACTIVE)`
- **Found Token:** `fWxhZXJfZXJhX3NleGlmZXJwX2RlY251b25uYV95bG5ve2Njamh0`

#### 2. Decoding the Token

The token retrieved from the registry is both Base64 encoded and reversed.

1.  **Base64 Decode**:
    `fWxhZXJfZXJhX3NleGlmZXJwX2RlY251b25uYV95bG5ve2Njamh0` $\rightarrow$ `flaer_era_sexiferp_decnuonna_ylnoy{ccjht`
2.  **Reverse String**:
    `flaer_era_sexiferp_decnuonna_ylnoy{ccjht` $\rightarrow$ `thjcc{yonly_announced_prefixes_are_real}`

#### 3. Automation

You can recover the flag using this quick one-liner:

```bash
echo "fWxhZXJfZXJhX3NleGlmZXJwX2RlY251b25uYV95bG5ve2Njamh0" | base64 -d | rev
```

---

### Flag

`thjcc{yonly_announced_prefixes_are_real}`
