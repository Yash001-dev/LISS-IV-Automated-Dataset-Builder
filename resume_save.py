import os
import json
import shutil
import subprocess
from datetime import datetime

from elevation_lookup import get_elevation

SCENE_FOLDER = r"F:\ISRO Hacathon\LISS_Web\uploads\scenes"
DATASET_FOLDER = r"C:\ISRO Hackathon\dataset"

metadata_path = os.path.join(
    SCENE_FOLDER,
    "metadata.json"
)

if not os.path.exists(
    metadata_path
):
    print(
        "metadata.json not found"
    )
    raise SystemExit

with open(
    metadata_path,
    "r"
) as f:

    scenes = json.load(f)

metadata_db = os.path.join(
    DATASET_FOLDER,
    "dataset_metadata.json"
)

if os.path.exists(
    metadata_db
):

    with open(
        metadata_db,
        "r"
    ) as f:

        dataset_metadata = json.load(f)

else:

    dataset_metadata = []

saved = 0

for scene in scenes:

    cloud_percent = scene[
        "cloud_percent"
    ]

    if cloud_percent < 10:
        category = "0-10"

    elif cloud_percent < 20:
        category = "10-20"

    elif cloud_percent < 30:
        category = "20-30"

    elif cloud_percent < 40:
        category = "30-40"

    elif cloud_percent < 50:
        category = "40-50"

    elif cloud_percent < 60:
        category = "50-60"

    elif cloud_percent < 70:
        category = "60-70"

    elif cloud_percent < 80:
        category = "70-80"

    elif cloud_percent < 90:
        category = "80-90"

    else:
        category = "90-100"

    category_folder = os.path.join(
        DATASET_FOLDER,
        category
    )

    os.makedirs(
        category_folder,
        exist_ok=True
    )

    base_name = (
        f"P{scene['path']}_"
        f"R{scene['row']}_"
        f"{scene['date']}"
    )

    destination = os.path.join(
        category_folder,
        f"{base_name}.tif"
    )

    counter = 1

    while os.path.exists(
        destination
    ):

        destination = os.path.join(
            category_folder,
            f"{base_name}_{counter}.tif"
        )

        counter += 1

    print(
        "Copying:",
        os.path.basename(
            destination
        )
    )

    shutil.copy(
        scene["combined"],
        destination
    )

    date_obj = datetime.strptime(
        scene["date"],
        "%Y_%m_%d"
    )

    month = date_obj.month

    if month in [12,1,2]:
        season = "winter"

    elif month in [3,4,5]:
        season = "pre_monsoon"

    elif month in [6,7,8,9]:
        season = "monsoon"

    else:
        season = "post_monsoon"

    try:

        lat = float(
            scene["scene_center_lat"]
        )

        lon = float(
            scene["scene_center_lon"]
        )

        elevation = get_elevation(
            lat,
            lon
        )

    except:

        elevation = 0

    snow_risk = False

    if (
        month in [12,1,2]
        and
        elevation > 2500
    ):

        snow_risk = True

    cloud_score = scene[
        "cloud_score"
    ]

    if snow_risk:

        cloud_score *= 0.7

    dataset_metadata.append({

        "file":
            os.path.basename(
                destination
            ),

        "tif_path":
            destination.replace(
                "\\",
                "/"
            ),

        "texture":
            scene["texture"],

        "category":
            category,

        "snow_risk":
            snow_risk,

        "elevation":
            elevation,

        "cloud_score":
            round(
                cloud_score,
                2
            ),

        "path":
            scene["path"],

        "row":
            scene["row"],

        "date":
            scene["date"],

        "year":
            date_obj.year,

        "month":
            date_obj.month,

        "season":
            season,

        "cloud_percent":
            scene["cloud_percent"],

        "scene_center_lat":
            scene["scene_center_lat"],

        "scene_center_lon":
            scene["scene_center_lon"],

        "ul_lat":
            scene["ul_lat"],

        "ul_lon":
            scene["ul_lon"],

        "ur_lat":
            scene["ur_lat"],

        "ur_lon":
            scene["ur_lon"],

        "lr_lat":
            scene["lr_lat"],

        "lr_lon":
            scene["lr_lon"],

        "ll_lat":
            scene["ll_lat"],

        "ll_lon":
            scene["ll_lon"],

        "satellite":
            scene["satellite"],

        "sensor":
            scene["sensor"],

        "product_id":
            scene["product_id"]

    })

    saved += 1

with open(
    metadata_db,
    "w"
) as f:

    json.dump(
        dataset_metadata,
        f,
        indent=4
    )

print()
print(
    f"Saved {saved} scenes"
)

print()
print(
    "Running Pipeline..."
)

subprocess.run(
    ["python","pipeline.py"],
    check=True
)

print()
print(
    "Pipeline Complete"
)