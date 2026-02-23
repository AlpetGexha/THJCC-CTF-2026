# Bit by Bit

**Point: 324**

### Description

The challenge performs a bit-by-bit encryption of a 105-byte secret string. For each bit:

- If the bit is **1**, a fixed 500-byte secret `key` is encrypted using RSA.
- If the bit is **0**, a random 500-byte value is encrypted using RSA.

The RSA moduli are small (64-bit), and the flag is encrypted using AES-CBC with a key derived from the 105-byte secret.

### Solution

1. **Factor RSA Moduli**: Since each $N = p \times q$ uses small 32-bit primes, we can easily factor all moduli and decrypt the RSA ciphertexts to retrieve the original 500-byte residues.
2. **Recover the Secret Key**:
   - The RSA samples corresponding to '1' bits all share the same 500-byte `key`.
   - The RSA samples corresponding to '0' bits are random.
   - We use the **LLL (Lenstra–Lenstra–Lovász) algorithm** on a lattice constructed from the Chinese Remainder Theorem (CRT) moments of these residues. This allows us to find the most likely candidate for the hidden 500-byte `key`.
3. **Reconstruct Secret Data**: By checking which decrypted residues match the recovered `key`, we identify the '1' and '0' bits of the original 105-byte secret.
4. **Decrypt Flag**: Deriving the AES key from the reconstructed secret allows us to decrypt the final flag.

### Flag

`THJCC{bit_by_bit_lll_is_powerful}`
