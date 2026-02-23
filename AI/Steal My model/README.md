# Steal My Model

**Point: 385**

### Description

The goal is to recover a hidden linear classifier defined by a 16-dimensional unit vector `n` and a scalar `beta`.

- Model: `label = 1 if dot(n, x) + beta >= 0 else 0`
- Success: Recover `n` and `beta` with error less than `0.005`.

### Vulnerability: Oracle Leak

While the challenge implies a black-box label attack, the `/submit` endpoint leaks precise error metrics on failure:

1. `max_component_error = max_i |n_guess[i] - n[i]|`
2. `beta_error = |beta_guess - beta|`

This distance oracle allows us to reconstruct the parameters directly without using the labels.

### Solution Strategy

1. **Recover Vector `n`**:
   - For each dimension `i`, submit guesses `v+ = 3.0 * e_i` and `v- = -3.0 * e_i`.
   - The errors will be `fp = 3.0 - n_i` and `fm = 3.0 + n_i`.
   - Calculate `n_i = (fm - fp) / 2`.
2. **Recover `beta`**:
   - Query with `beta_guess = 0` to get `d0 = |beta|`.
   - Query with `beta_guess = 1` to get `d1 = |1 - beta|`.
   - Solve for the sign of `beta` using these distances.
3. **Submit**: Use the recovered `n` and `beta` for the final submission.

### Flag

`THJCC{y0ur_st3al1ng_sk1ll_1s_amaz1ng}`
