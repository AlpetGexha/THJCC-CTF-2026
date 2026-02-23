# 676767

**100**

676767 67 6767

67 EVERYWHERE 0A0
Just bring me out of this 67 haven ...

Author: whale120

nc chal.thjcc.org 48764

### Vulnerability: Seed Replay

Python's `random.seed()` treats negative integers such that `random.seed(-x)` can result in the same internal state as `random.seed(x)`. By sending `a = -1` and `b = 0`, we effectively reset the generator to its initial state.

### Solution

1. **Leaked Values**: Capture the first 10 numbers generated.
2. **Reset State**: Send `a = -1` and `b = 0` to trigger `random.seed(-seed)`.
3. **Replay**: Provide the captured numbers as answers.
4. **Retry**: Since `randrange(base)` uses rejection sampling, the replay only works if all captured numbers are less than `base`. Retry until this condition is met.

The seed was 70 :)

### Flag

`THJCC{676767676767676767676767_i_dont_like_those_brainnot_memes_XD}`
