import json
import os
import rasterio
from rasterio.windows import from_bounds

# Create output folder
os.makedirs(
    "aligned",
    exist_ok=True
)

# Load training pairs
with open(
    r"C:\ISRO Hackathon\dataset\training_pairs.json",
    "r"
) as f:

    training_pairs = json.load(f)

for index, pair in enumerate(training_pairs, start=1):

    cloudy_path = pair["cloudy_tif_path"]
    clear_path = pair["clear_tif_path"]

    cloudy_name = os.path.splitext(
        pair["cloudy_file"]
    )[0]
    
    clear_name = os.path.splitext(
        pair["clear_file"]
    )[0]

    pair_folder = os.path.join(
        "aligned",
        f"{cloudy_name}__{clear_name}"
    )

    if os.path.exists(
        pair_folder
    ):

        print(
          f"Skipping {os.path.basename(pair_folder)}"
        )

        continue

    os.makedirs(
        pair_folder,
        exist_ok=True
    )

    print(
        f"\nProcessing Pair {index}"
    )

    with rasterio.open(cloudy_path) as cloudy:

        cloudy_bounds = cloudy.bounds

    with rasterio.open(clear_path) as clear:

        clear_bounds = clear.bounds

    # Find common area
    common_left = max(
        cloudy_bounds.left,
        clear_bounds.left
    )

    common_bottom = max(
        cloudy_bounds.bottom,
        clear_bounds.bottom
    )

    common_right = min(
        cloudy_bounds.right,
        clear_bounds.right
    )

    common_top = min(
        cloudy_bounds.top,
        clear_bounds.top
    )

    # Save cloudy crop
    with rasterio.open(cloudy_path) as cloudy:

        cloudy_window = from_bounds(
            common_left,
            common_bottom,
            common_right,
            common_top,
            cloudy.transform
        )

        cloudy_data = cloudy.read(
            window=cloudy_window
        )

        cloudy_profile = cloudy.profile.copy()

        cloudy_profile.update(

            width=int(
                cloudy_window.width
            ),

            height=int(
                cloudy_window.height
            ),

            transform=rasterio.windows.transform(
                cloudy_window,
                cloudy.transform
            )

        )

        cloudy_output = os.path.join(
            pair_folder,
            "cloudy.tif"
        )

        with rasterio.open(
            cloudy_output,
            "w",
            **cloudy_profile
        ) as dst:

            dst.write(
                cloudy_data
            )

    # Save clear crop
    with rasterio.open(clear_path) as clear:

        clear_window = from_bounds(
            common_left,
            common_bottom,
            common_right,
            common_top,
            clear.transform
        )

        clear_data = clear.read(
            window=clear_window
        )

        clear_profile = clear.profile.copy()

        clear_profile.update(

            width=int(
                clear_window.width
            ),

            height=int(
                clear_window.height
            ),

            transform=rasterio.windows.transform(
                clear_window,
                clear.transform
            )

        )

        clear_output = os.path.join(
            pair_folder,
            "clear.tif"
        )

        with rasterio.open(
            clear_output,
            "w",
            **clear_profile
        ) as dst:

            dst.write(
                clear_data
            )

    # Save pair metadata
    with open(
        os.path.join(
            pair_folder,
            "metadata.json"
        ),
        "w"
    ) as f:

        json.dump(
            pair,
            f,
            indent=4
        )

    print(
        f"Saved {pair_folder}"
    )

print(
    "\nAll pairs processed."
)