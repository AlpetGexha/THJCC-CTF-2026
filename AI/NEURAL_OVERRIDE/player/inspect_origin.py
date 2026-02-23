
import torch
from model_loader import DynamicModel

def inspect():
    model = DynamicModel("model.json")
    model.load_state_dict(torch.load("model.pth", map_location="cpu"))
    model.eval()
    
    origin = torch.load("origin.pt", map_location="cpu")
    print(f"Origin shape: {origin.shape}")
    
    with torch.no_grad():
        output = model(origin)
        probs = torch.softmax(output, dim=1)
        conf, pred = torch.max(probs, 1)
        print(f"Original Pred: {pred.item()}, Confidence: {conf.item():.4f}")
        print(f"Original Output: {output}")

if __name__ == "__main__":
    inspect()
