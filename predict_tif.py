import torch
import rasterio
import numpy as np
import matplotlib.pyplot as plt

from model import UNet

DEVICE = "cpu"

# -------------------
# Load Model
# -------------------

model = UNet()

model.load_state_dict(
    torch.load(
        "models/best_model.pth",
        map_location=DEVICE
    )
)

model.eval()

# -------------------
# Load TIFF
# -------------------

tif_path = r"F:\image.tif"

with rasterio.open(tif_path) as src:

    img = src.read()

print("Original Shape:", img.shape)
print("Data Type:", img.dtype)

# Convert from:
# (bands, height, width)
# to
# (height, width, bands)

img = np.transpose(
    img,
    (1, 2, 0)
)

# -------------------
# Extract Center Patch
# -------------------

h, w, _ = img.shape

y = h // 2
x = w // 2

patch = img[
    y:y+256,
    x:x+256,
    :3
]

print("Patch Shape:", patch.shape)
print("Patch Min:", patch.min())
print("Patch Max:", patch.max())

# -------------------
# Display Version
# -------------------

display_patch = patch.astype(
    np.float32
)

display_patch = (
    display_patch
    -
    display_patch.min()
)

display_patch = (
    display_patch
    /
    (
        display_patch.max()
        +
        1e-8
    )
)

# -------------------
# Model Input Version
# -------------------

model_patch = patch.astype(
    np.float32
)

model_patch = (
    model_patch
    -
    model_patch.min()
)

model_patch = (
    model_patch
    /
    (
        model_patch.max()
        +
        1e-8
    )
)

# -------------------
# Prediction
# -------------------

x_tensor = torch.tensor(
    model_patch.transpose(2, 0, 1)
).unsqueeze(0)

with torch.no_grad():

    pred = model(
        x_tensor
    )

pred = pred.squeeze().numpy()

pred = pred.transpose(
    1,
    2,
    0
)

# -------------------
# Show Results
# -------------------

plt.figure(
    figsize=(14, 6)
)

plt.subplot(1, 2, 1)

plt.imshow(
    display_patch
)

plt.title(
    "Cloudy Input"
)

plt.subplot(1, 2, 2)

plt.imshow(
    pred.clip(0, 1)
)

plt.title(
    "Model Prediction"
)

plt.tight_layout()

plt.show()