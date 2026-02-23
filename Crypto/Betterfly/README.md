# Butterfly

**Point: 182**
They say a butterfly's wings can cause a tornado halfway around the world. This cipher embraces that chaos. Can you find the key that unlocks the secret?

the initial key lead to completely different results.

### Solution

1. **Analyze the Cipher**: The encryption uses a chaotic logistic map (`x = r * x * (1 - x)`) to generate a keystream.
2. **Determine the Key**: By mapping the known prefix `THJCC{` to the ciphertext, we can deduce or test the initial float key (found to be `0.123456789`).
3. **Decrypt**: Perform the bitwise XOR operation with the generated keystream.
4. **Post-Process**: The resulting text is further obfuscated with a Caesar cipher (Shift: 11). Applying the shift reveals the final flag.

### Flag

`THJCC{N07hinGbEat5aJ2h0liDaye}`
