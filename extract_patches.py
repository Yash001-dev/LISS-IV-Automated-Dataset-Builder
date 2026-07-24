import os
import rasterio
import numpy as np
import json

PATCH_SIZE = 256

os.makedirs(
    "patches/cloudy",
    exist_ok=True
)


os.makedirs(
    "patches/clear",
    exist_ok=True
)

if not os.path.exists("aligned"):
    raise Exception("aligned folder not found")

pair_folders = sorted(

    [

        os.path.join(
            "aligned",
            folder
        )

        for folder in os.listdir(
            "aligned"
        )

        if os.path.isdir(
            os.path.join(
                "aligned",
                folder
            )
        )

    ]

)

print(
    f"Found {len(pair_folders)} pairs"
)
if os.path.exists(
    "processed_pairs.json"
):

    with open(
        "processed_pairs.json",
        "r"
    ) as f:

        processed_pairs = set(
            json.load(f)
        )

else:

    processed_pairs = set()

print(
    f"Already processed pairs: {len(processed_pairs)}"
)

existing_patches = [

    f for f in os.listdir(
        "patches/cloudy"
    )

    if f.startswith("patch_")
    and f.endswith(".npy")

]

cloudy_count = len(
    os.listdir("patches/cloudy")
)

clear_count = len(
    os.listdir("patches/clear")
)

if cloudy_count != clear_count:

    raise Exception(
        "Cloudy/Clear patch count mismatch"
    )


if len(existing_patches) == 0:

    patch_id = 1

else:

    patch_numbers = [

        int(
            f.replace(
                "patch_",
                ""
            ).replace(
                ".npy",
                ""
            )
        )

        for f in existing_patches

    ]

    patch_id = max(
        patch_numbers
    ) + 1

print(
    f"Next patch ID: {patch_id}"
)

print(
    f"Starting from Patch ID {patch_id}"
)

saved_patches = 0
rejected_patches = 0
print(
    f"Existing patches: {len(existing_patches)}"
)

print(
    f"Next patch ID: {patch_id}"
)

for pair_folder in pair_folders:

    pair_name = os.path.basename(
        pair_folder
    )

    if pair_name in processed_pairs:

        print(
            f"Skipping {pair_name}"
        )

        continue

    cloudy_path = os.path.join(
        pair_folder,
        "cloudy.tif"
    )

    clear_path = os.path.join(
        pair_folder,
        "clear.tif"
    )

    print(
        f"\nProcessing {pair_folder}"
    )

    with rasterio.open(
        cloudy_path
    ) as cloudy_src, rasterio.open(
        clear_path
    ) as clear_src:

        width = min(
            cloudy_src.width,
            clear_src.width
        )

        height = min(
            cloudy_src.height,
            clear_src.height
        )

        for y in range(
            0,
            height - PATCH_SIZE + 1,
            PATCH_SIZE
        ):

            for x in range(
                0,
                width - PATCH_SIZE + 1,
                PATCH_SIZE
            ):

                cloudy_patch = cloudy_src.read(

                    window=((

                        y,
                        y + PATCH_SIZE

                    ), (

                        x,
                        x + PATCH_SIZE

                    ))

                )

                clear_patch = clear_src.read(

                    window=((

                        y,
                        y + PATCH_SIZE

                    ), (

                        x,
                        x + PATCH_SIZE

                    ))

                )

                # -------------------------
                # Remove NoData patches
                # -------------------------

                # Better NoData detection
                clear_black_pixels = np.sum(

                    np.all(
                        clear_patch == 0,
                        axis=0
                    )

                )

                cloudy_mask = np.all(
                    cloudy_patch <= 5,
                    axis=0
                )

                clear_mask = np.all(
                    clear_patch <= 5,
                    axis=0
                )

                cloudy_black_ratio = np.mean(cloudy_mask)
                clear_black_ratio = np.mean(clear_mask)

                cloudy_black_pixels = np.sum(np.all(cloudy_patch == 0, axis=0))
                clear_black_pixels = np.sum(np.all(clear_patch == 0, axis=0))

                # fallback to pixel-count ratio if needed
                if cloudy_black_pixels > 0:
                    cloudy_black_ratio = cloudy_black_pixels / (PATCH_SIZE * PATCH_SIZE)
                if clear_black_pixels > 0:
                    clear_black_ratio = clear_black_pixels / (PATCH_SIZE * PATCH_SIZE)

                if cloudy_black_ratio > 0.10:
                    rejected_patches += 1
                    continue

                if clear_black_ratio > 0.10:
                    rejected_patches += 1
                    continue

                # Reject empty patches
                if np.std(cloudy_patch) < 1:
                    rejected_patches += 1
                    continue

                if np.std(clear_patch) < 1:
                    rejected_patches += 1
                    continue

                patch_name = (
                    f"patch_{patch_id:06d}.npy"
                )

                np.save(

                    os.path.join(
                        "patches/cloudy",
                        patch_name
                    ),

                    cloudy_patch

                )

                np.save(

                    os.path.join(
                        "patches/clear",
                        patch_name
                    ),

                    clear_patch

                )

                saved_patches += 1

                patch_id += 1


                if saved_patches % 1000 == 0:

                    print(
                        f"Saved {saved_patches} patches"
                    )

    # Same indentation as "with rasterio.open"
    processed_pairs.add(
        pair_name
    )

    print(
        f"Completed {pair_name}"
    )

# <-- End of for pair_folder loop

with open(
    "processed_pairs.json",
    "w"
) as f:

    json.dump(
        sorted(
            list(processed_pairs)
        ),
        f,
        indent=4
    )

print()
print(
    f"Saved patches: {saved_patches}"
)

print(
    f"Rejected patches: {rejected_patches}"
)

print(
    f"Total checked: "
    f"{saved_patches + rejected_patches}"
)