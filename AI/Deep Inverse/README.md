# Deep Inverse

**Point: 100**

### Description

Input: x (10-dim vector)

Goal: f(x) ≈ 1337.0

The system is watching. Can you find the input that satisfies the model?

Author: Auron

nc chal.thjcc.org 1337

### Solution

To solve this challenge, we perform a gradient-based "inverse" of the model:

1.  **Load the Model**: Use `torch.jit.load` to load the provided `model.pt` file.
2.  **Define the Target**: Our goal is to find an input `x` such that the model output is `1337.0`.
3.  **Optimize the Input**:
    - Initialize a random 10-dimensional tensor `x` with gradients enabled.
    - Use an optimizer (like **Adam**) to minimize the loss: `loss = (model(x) - 1337.0)^2`.
    - Iterate until the model output is sufficiently close to the target.
4.  **Submit Solution**: Send the optimized vector as a comma-separated string to the remote server.
