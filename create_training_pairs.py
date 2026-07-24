import json
import os

print("=" * 50)
print("Current folder:")
print(os.getcwd())
print("=" * 50)

metadata_file = os.path.join(
    "dataset",
    "C:\ISRO Hackathon\dataset\dataset_metadata.json"
)

overlap_file = os.path.join(
    "dataset",
    "C:\ISRO Hackathon\dataset\overlap_matches.json"
)

print(
    "Dataset folder exists:",
    os.path.exists("dataset")
)

print(
    "Metadata file exists:",
    os.path.exists(metadata_file)
)

print(
    "Overlap file exists:",
    os.path.exists(overlap_file)
)

if not os.path.exists(
    metadata_file
):

    print("\nERROR:")
    print(metadata_file)
    print("not found")

    raise SystemExit

if not os.path.exists(
    overlap_file
):

    print("\nERROR:")
    print(overlap_file)
    print("not found")

    raise SystemExit

# Load metadata

with open(
    metadata_file,
    "r"
) as f:

    metadata = json.load(f)

# Build filename -> tif path lookup

file_to_path = {}

for scene in metadata:

    file_to_path[
        scene["file"]
    ] = scene["tif_path"]

# Load overlap matches

with open(
    overlap_file,
    "r"
) as f:

    matches = json.load(f)

training_pairs = []

for match in matches:
    print()
    print(match["file_a"])
    print(match["file_b"])

    print(
        "cloud_a:",
        match["cloud_a"]
    )

    print(
        "cloud_b:",
        match["cloud_b"]
    )

    cloud_a = match["cloud_a"]
    cloud_b = match["cloud_b"]

    # Decide cloudy and clear image

    if cloud_a >= cloud_b:

        cloudy_file = match["file_a"]
        clear_file = match["file_b"]

        cloudy_percent = cloud_a
        clear_percent = cloud_b

    else:

        cloudy_file = match["file_b"]
        clear_file = match["file_a"]

        cloudy_percent = cloud_b
        clear_percent = cloud_a

    # Clear image must be reasonably cloud-free

    if clear_percent > 20:

        print(
            "Rejected: clear > 20"
        )

        continue

    # Cloudy image should be significantly cloudier

    if (
        cloudy_percent
        -
        clear_percent
    ) < 10:

        print(
            "Rejected: cloud diff < 10"
        )

        continue

    # Cloudy image must actually be cloudy

    if cloudy_percent < 15:

        print(
            "Rejected: cloudy < 15"
        )

        continue

    training_pairs.append({

        "cloudy_file":
            cloudy_file,

        "cloudy_tif_path":
            file_to_path[cloudy_file],

        "clear_file":
            clear_file,

        "clear_tif_path":
            file_to_path[clear_file],

        "cloudy_percent":
            cloudy_percent,

        "clear_percent":
            clear_percent,

        "overlap_percent":
            match["overlap_percent"],

        "days_difference":
            match["days_difference"],

        "season":
            match["season"],

        "snow_risk_a":
            match.get(
                "snow_risk_a",
                False
            ),

        "snow_risk_b":
            match.get(
                "snow_risk_b",
                False
            ),
        "elevation_a":
            match.get(
                "elevation_a",
                -9999
            ),
        "elevation_b":
            match.get(
                "elevation_b",
                -9999
            ),

    })

# Save training pairs

with open(
    r"C:\ISRO Hackathon\dataset\training_pairs.json",
    "w"
) as f:

    json.dump(
        training_pairs,
        f,
        indent=4
    )

print()

print(
    f"Saved {len(training_pairs)} training pairs"
)