from pwn import *
import torch
import torch.optim as optim

# =========================
# Load TorchScript model
# =========================
model = torch.jit.load("model.pt", map_location="cpu")
model.eval()

# =========================
# Optimize 10-dim input
# =========================
x = torch.randn(1, 10) * 100
x.requires_grad_()

target = torch.tensor([1337.0])
optimizer = optim.Adam([x], lr=1.0)

for step in range(20000):
    optimizer.zero_grad()
    output = model(x)
    loss = (output - target).pow(2)
    loss.backward()
    optimizer.step()

final_output = model(x).item()
final_vector = x.detach().tolist()[0]

print("Final output:", final_output)
print("Final vector:", final_vector)

# =========================
# Prepare payload (FULL precision)
# =========================
payload = ",".join(str(v) for v in final_vector)

# =========================
# Connect to remote service
# =========================
conn = remote("chal.thjcc.org", 1337)

# Receive full banner
print(conn.recvrepeat(1).decode())

# Send solution
conn.sendline(payload.encode())

# Receive full response
print(conn.recvall(timeout=3).decode())

conn.close()