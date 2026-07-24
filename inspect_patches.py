import os
import random
import numpy as np
import matplotlib.pyplot as plt

cloudy_dir = "patches/cloudy"
clear_dir = "patches/clear"

patches = sorted(
    os.listdir(cloudy_dir)
)

sample = random.choice(
    patches
)

cloudy = np.load(
    os.path.join(
        cloudy_dir,
        sample
    )
)

clear = np.load(
    os.path.join(
        clear_dir,
        sample
    )
)

cloudy = np.transpose(
    cloudy,
    (1, 2, 0)
)

clear = np.transpose(
    clear,
    (1, 2, 0)
)

cloudy = cloudy.astype(
    np.float32
)

clear = clear.astype(
    np.float32
)

cloudy = (
    cloudy - cloudy.min()
) / (
    cloudy.max() - cloudy.min() + 1e-6
)

clear = (
    clear - clear.min()
) / (
    clear.max() - clear.min() + 1e-6
)

plt.figure(
    figsize=(10, 5)
)

plt.subplot(
    1,
    2,
    1
)

plt.imshow(
    cloudy
)

plt.title(
    f"Cloudy\n{sample}"
)

plt.axis(
    "off"
)

plt.subplot(
    1,
    2,
    2
)

plt.imshow(
    clear
)

plt.title(
    f"Clear\n{sample}"
)

plt.axis(
    "off"
)

plt.show()