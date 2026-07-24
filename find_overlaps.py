import os
import json
from datetime import datetime
from shapely.geometry import Polygon

with open(
    "C:\ISRO Hackathon\dataset\dataset_metadata.json",
    "r"
) as f:

    scenes = json.load(f)

# Load existing matches

if os.path.exists(
    "C:\ISRO Hackathon\dataset\overlap_matches.json"
):

    with open(
        "C:\ISRO Hackathon\dataset\overlap_matches.json",
        "r"
    ) as f:

        matches = json.load(f)

else:

    matches = []

# Build cache of existing pairs

existing_pairs = set()

for match in matches:

    pair = tuple(

        sorted([

            match["file_a"],
            match["file_b"]

        ])

    )

    existing_pairs.add(
        pair
    )


def scene_polygon(scene):
    required = [

        scene["ul_lat"],
        scene["ul_lon"],
        scene["ur_lat"],
        scene["ur_lon"],
        scene["lr_lat"],
        scene["lr_lon"],
        scene["ll_lat"],
        scene["ll_lon"]

    ]

    if any(v is None for v in required):

        return None
    return Polygon([

        (
            float(scene["ul_lon"]),
            float(scene["ul_lat"])
        ),

        (
            float(scene["ur_lon"]),
            float(scene["ur_lat"])
        ),

        (
            float(scene["lr_lon"]),
            float(scene["lr_lat"])
        ),

        (
            float(scene["ll_lon"]),
            float(scene["ll_lat"])
        )

    ])


new_matches = 0

for i in range(len(scenes)):

    for j in range(i + 1, len(scenes)):

        scene_a = scenes[i]
        scene_b = scenes[j]

        pair = tuple(

            sorted([

                scene_a["file"],
                scene_b["file"]

            ])

        )

        # Skip already processed pairs

        if pair in existing_pairs:

            continue



        # Same Season

        if scene_a["season"] != scene_b["season"]:

            continue

        # Date Difference

        date_a = datetime.strptime(
            scene_a["date"],
            "%Y_%m_%d"
        )

        date_b = datetime.strptime(
            scene_b["date"],
            "%Y_%m_%d"
        )

        days_diff = abs(
            (date_a - date_b).days
        )



        poly_a = scene_polygon(scene_a)
        poly_b = scene_polygon(scene_b)
        if poly_a is None:

         continue

        if poly_b is None:

         continue

        intersection = poly_a.intersection(
            poly_b
        )

        if intersection.area == 0:

            overlap = 0

        else:

            overlap = (
                intersection.area
                /
                min(
                    poly_a.area,
                    poly_b.area
                )

            ) * 100

        if overlap >= 50:

            matches.append({

                "file_a":
                    scene_a["file"],

                "file_b":
                    scene_b["file"],

                "cloud_a":
                    scene_a.get(
                        "cloud_score",
                        scene_a["cloud_percent"]
                    ),

                "cloud_b":
                    scene_b.get(
                        "cloud_score",
                        scene_b["cloud_percent"]
                    ),

                "snow_risk_a":
                    scene_a.get(
                        "snow_risk",
                        False
                    ),

                "snow_risk_b":
                    scene_b.get(
                        "snow_risk",
                        False
                    ),
                
                "elevation_a":
                    scene_a["elevation"],
                "elevation_b":
                    scene_b["elevation"],
                "snow_risk_a":
                    scene_a["snow_risk"],
                "snow_risk_b":
                    scene_b["snow_risk"],
                    

                "overlap_percent":
                    round(
                        overlap,
                        2
                    ),

                "days_difference":
                    days_diff,

                "season":
                    scene_a["season"]

            })

            existing_pairs.add(
                pair
            )

            new_matches += 1

with open(
    "C:\ISRO Hackathon\dataset\overlap_matches.json",
    "w"
) as f:

    json.dump(
        matches,
        f,
        indent=4
    )

print()

print(
    f"New matches added: {new_matches}"
)

print(
    f"Total matches stored: {len(matches)}"
)