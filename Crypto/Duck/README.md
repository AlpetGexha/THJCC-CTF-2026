# Duck (Crypto)

**Point: 496**

The challenge involves multiple layers of classical cryptography.

## Solution Steps

### Layer 1: Formatting

The input lines in `secret.txt` are mostly reversed. We can tell because sentences end with `.` at the beginning and start with a capital letter at the end.

### Layer 2: Caesar Cipher

All text is shifted by **+12**. This shift is consistent across all sections.

### Layer 3: Vigenère Cipher

The key for the Vigenère layer is **`sword`**. Different parts of the text use different rotations of this key (e.g., `words`, `dswor`).

### Layer 4: Base64

The long middle string is a **Reversed Base64** payload. After stripping the leading `=` and reversing, we apply the Caesar and Vigenère layers to reveal the Base64-encoded text.

### Layer 5: Monoalphabetic Substitution

The final message revealed after the Base64 layer is still encrypted with a simple substitution cipher (each letter maps to a unique fixed replacement). We broke this using **Crib-Dragging**—the process of identifying known words ("cribs") based on their character patterns and positions.

#### Step 1: Solving the "the" and "of"

We looked for high-frequency 3-letter and 2-letter words.

- The word **`smr`** appeared multiple times in positions where "the" would be expected.
  - **Deduction:** `s` $\rightarrow$ `t`, `m` $\rightarrow$ `h`, `r` $\rightarrow$ `e`.
- The word **`jy`** appeared frequently.
  - **Deduction:** `j` $\rightarrow$ `o`, `y` $\rightarrow$ `f` (yielding "of").

#### Step 2: Pattern Matching for Long Words

Once we had the basic structure, we looked at longer, unique words.

- **`Djcfepszopstjcl`**: This 15-letter word has the pattern of **"Congratulations"**.
  - **Mapping:** `D` $\rightarrow$ `C`, `j` $\rightarrow$ `o`, `c` $\rightarrow$ `n`, `f` $\rightarrow$ `g`, `e` $\rightarrow$ `r`, `p` $\rightarrow$ `a`, `s` $\rightarrow$ `t`, `z` $\rightarrow$ `d`, `o` $\rightarrow$ `l`, `p` $\rightarrow$ `a`, `s` $\rightarrow$ `t`, `t` $\rightarrow$ `i`, `j` $\rightarrow$ `o`, `c` $\rightarrow$ `n`, `l` $\rightarrow$ `s`.
- This confirmed our previous deductions and gave us nearly half the alphabet.

#### Step 3: Contextual Deductions

The article mentioned Alan Turing. We found a sequence:

- **`tvqejgr smr otgrl jy jsmrel`**
- Applying current mappings: `_vpe_re the l_ves of othe_s`
- It clearly decodes to: **"improve the lives of others"**
  - **Mapping:** `t` $\rightarrow$ `i`, `v` $\rightarrow$ `m`, `q` $\rightarrow$ `p`, `g` $\rightarrow$ `v`.

#### Step 4: Final Flag Recovery

Applying all the discovered mappings to the flag line:

- `SMADD{d1@ll1d41_deb9s0fe@9mb_1l_l1v9or_e1fm7?}`
- Decodes to: `THJCC{c1@ss1c41_cry9t0gr@9hy_1s_s1m9le_r1gh7?}`
- (Substitution: `S` $\rightarrow$ `T`, `M` $\rightarrow$ `H`, `A` $\rightarrow$ `J`, `D` $\rightarrow$ `C`)

### Final Flag

`THJCC{c1@ss1c41_cry9t0gr@9hy_1s_s1m9le_r1gh7?}`
