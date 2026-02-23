
import torch
import torchvision.transforms as T
from PIL import Image

def save_as_img():
    origin = torch.load("origin.pt", map_location="cpu")
    # origin is likely [1, 3, 32, 32]
    # Remove batch dim
    tensor = origin.squeeze(0)
    # Clamp to [0, 1] if needed, but let's see range first
    print(f"Range: {tensor.min().item()} to {tensor.max().item()}")
    
    # Assuming it's already in [0, 1] or similar
    # If it's normalized, we might need to unnormalize, but let's try direct first
    to_pil = T.ToPILImage()
    img = to_pil(tensor.cpu())
    img.save("origin_debug.png")

if __name__ == "__main__":
    save_as_img()
