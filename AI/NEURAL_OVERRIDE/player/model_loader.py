import torch
import torch.nn as nn

class DynamicModel(nn.Module):
    def __init__(self, config_or_path):
        super(DynamicModel, self).__init__()
        
        if isinstance(config_or_path, str):
            import json
            with open(config_or_path, "r") as f:
                self.config = json.load(f)
        else:
            self.config = config_or_path
            
        self.layers = nn.ModuleList()
        self._build_model()

    def _build_model(self):
        for layer_def in self.config:
            lt = layer_def['type']
            p = layer_def['params']
            
            if lt == "Conv2d":
                self.layers.append(nn.Conv2d(**p))
            elif lt == "BatchNorm2d":
                self.layers.append(nn.BatchNorm2d(**p))
            elif lt == "MaxPool2d":
                self.layers.append(nn.MaxPool2d(**p))
            elif lt == "Linear":
                self.layers.append(nn.Linear(**p))
            elif lt == "ReLU":
                self.layers.append(nn.ReLU())
            elif lt == "Flatten":
                self.layers.append(nn.Flatten())
            elif lt == "Dropout":
                self.layers.append(nn.Dropout(**p))
            else:
                raise ValueError(f"Unknown layer type: {lt}")

    def forward(self, x):
        for layer in self.layers:
            x = layer(x)
        return x