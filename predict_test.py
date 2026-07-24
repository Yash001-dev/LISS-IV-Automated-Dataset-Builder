import torch

from model import UNet

DEVICE = "cpu"

model = UNet()

model.load_state_dict(
    torch.load(
        "models/best_model.pth",
        map_location=DEVICE
    )
)

model.eval()

x = torch.rand(
    1,
    3,
    256,
    256
)

with torch.no_grad():

    y = model(x)

print(
    "Input shape:",
    x.shape
)

print(
    "Output shape:",
    y.shape
)