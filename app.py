from flask import Flask, render_template, request
from datetime import datetime
from elevation_lookup import (
    get_elevation
)
import os
import shutil
import zipfile
import re
import json
import rasterio
import numpy as np
import matplotlib.pyplot as plt
import subprocess
import time


app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
STATIC_FOLDER = "static"
SCENE_FOLDER = os.path.join(
UPLOAD_FOLDER,
"scenes"
)
DATASET_FOLDER = r"C:\ISRO Hackathon\dataset"
PREVIEW_SCALE = 8

os.makedirs(
UPLOAD_FOLDER,
exist_ok=True
)


os.makedirs(
STATIC_FOLDER,
exist_ok=True
)

os.makedirs(
SCENE_FOLDER,
exist_ok=True
)

os.makedirs(
DATASET_FOLDER,
exist_ok=True
)

@app.route("/")
def upload_page():
    return render_template(
        "upload.html"
    )

def extract_date(zip_name):
    zip_name = zip_name.upper()

    match = re.search(
        r'(\d{2})(JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)(\d{4})',
        zip_name
    )

    if not match:
        return "unknown"

    months = {
        "JAN":"01",
        "FEB":"02",
        "MAR":"03",
        "APR":"04",
        "MAY":"05",
        "JUN":"06",
        "JUL":"07",
        "AUG":"08",
        "SEP":"09",
        "OCT":"10",
        "NOV":"11",
        "DEC":"12"
    }

    day = match.group(1)
    month = months[
        match.group(2)
    ]
    year = match.group(3)

    return f"{year}_{month}_{day}"
def calculate_cloud_percent(rgb):

    rgb_norm = (
        rgb - rgb.min()
    ) / (
        rgb.max() - rgb.min() + 1e-8
    )

    r = rgb_norm[:, :, 0]
    g = rgb_norm[:, :, 1]
    b = rgb_norm[:, :, 2]

    valid_mask = (
        (r > 0.01)
        |
        (g > 0.01)
        |
        (b > 0.01)
    )

    brightness = (
        r + g + b
    ) / 3

    whiteness = (
        np.abs(r - g)
        + np.abs(r - b)
        + np.abs(g - b)
    )
    gray = brightness

    texture = np.std(
        gray
    )

    cloud_mask = (
        (brightness > 0.55)
        &
        (whiteness < 0.25)
    )

    valid_pixels = np.sum(
        valid_mask
    )

    if valid_pixels == 0:
        return 0

    cloud_pixels = np.sum(
        cloud_mask & valid_mask
    )

    cloud_percent = (
        cloud_pixels
        / valid_pixels
    ) * 100

    cloud_score = cloud_percent

    if texture > 0.25:

        cloud_score *= 0.9


    return (
        cloud_percent,
        cloud_score,
        texture
    )    


def get_cloud_category(percent):

    if percent < 10:
        return "0-10"

    elif percent < 20:
        return "10-20"

    elif percent < 30:
        return "20-30"

    elif percent < 40:
        return "30-40"

    elif percent < 50:
        return "40-50"

    elif percent < 60:
        return "50-60"

    elif percent < 70:
        return "60-70"

    elif percent < 80:
        return "70-80"

    elif percent < 90:
        return "80-90"

    return "90-100"

def find_meta_file(folder):

    for root, dirs, files in os.walk(folder):

        for file in files:

            if file.upper() == "BAND_META.TXT":

                return os.path.join(
                    root,
                    file
                )

    return None

def read_band_meta(meta_path):

    metadata = {}

    with open(
        meta_path,
        "r",
        encoding="utf-8",
        errors="ignore"
    ) as f:

        for line in f:

            if "=" not in line:
                continue

            key, value = line.split(
                "=",
                1
            )

            metadata[
                key.strip()
            ] = value.strip()

    return metadata

def find_band_files(folder):
    band2 = None
    band3 = None
    band4 = None

    for root, dirs, files in os.walk(folder):

        for file in files:

            name = file.upper()

            full_path = os.path.join(
                root,
                file
            )

            if "BAND2" in name:
                band2 = full_path

            elif "BAND3" in name:
                band3 = full_path

            elif "BAND4" in name:
                band4 = full_path

    return band2, band3, band4

@app.route("/preview", methods=["POST"])
def preview():
    if os.path.exists(SCENE_FOLDER):
        shutil.rmtree(SCENE_FOLDER)

    os.makedirs(
        SCENE_FOLDER,
        exist_ok=True
    )

    zip_files = request.files.getlist("zip_files")

    zip_files = [
        z for z in zip_files
        if z and z.filename.lower().endswith(".zip")
    ]

    if len(zip_files) == 0:
        return "No ZIP files selected."

    if len(zip_files) > 500:
        return "Maximum 500 ZIP files allowed."

    scenes = []

    for i, zip_file in enumerate(zip_files):
        start_time = time.time()

        scene_folder = os.path.join(
            SCENE_FOLDER,
            f"scene_{i}"
        )

        os.makedirs(
            scene_folder,
            exist_ok=True
        )

        zip_path = os.path.join(
            scene_folder,
            zip_file.filename
        )

        zip_file.save(zip_path)

        scene_date = extract_date(
            zip_file.filename
        )

        extract_folder = os.path.join(
            scene_folder,
            "extract"
        )

        os.makedirs(
            extract_folder,
            exist_ok=True
        )

        with zipfile.ZipFile(
            zip_path,
            "r"
        ) as z:

            z.extractall(
                extract_folder
            )
            print(
                f"ZIP Extract: {time.time()-start_time:.1f}s"
            )

        band2_path, band3_path, band4_path = find_band_files(
            extract_folder
        )
        meta_file = find_meta_file(
            extract_folder
        )

        metadata = {}

        if meta_file:
            metadata = read_band_meta(
                meta_file
            )
            print("\n===== METADATA =====")
            print(
                metadata.get("Path"),
                metadata.get("Row")
            )
            print(
                metadata.get("SceneCenterLat"),
                metadata.get("SceneCenterLon")
            )

        if not all([
            band2_path,
            band3_path,
            band4_path
        ]):
            continue

        with rasterio.open(
            band2_path
        ) as src2:

            band2_data = src2.read(1)

            profile = src2.profile

        with rasterio.open(
            band3_path
        ) as src3:

            band3_data = src3.read(1)

        with rasterio.open(
            band4_path
        ) as src4:

            band4_data = src4.read(1)

        band2_preview = band2_data[
            ::PREVIEW_SCALE,
            ::PREVIEW_SCALE
        ]

        band3_preview = band3_data[
            ::PREVIEW_SCALE,
            ::PREVIEW_SCALE
        ]

        band4_preview = band4_data[
            ::PREVIEW_SCALE,
            ::PREVIEW_SCALE
        ]
        print(
            f"Bands Read: {time.time()-start_time:.1f}s"
        )
        
        profile.update(
            count=3
        )

        combined_path = os.path.join(
            scene_folder,
            "combined.tif"
        )

        with rasterio.open(
            combined_path,
            "w",
            **profile
        ) as dst:

            dst.write(
                band4_data,
                1
            )

            dst.write(
                band3_data,
                2
            )

            dst.write(
                band2_data,
                3
            )
        rgb = np.dstack([
            band4_preview,
            band3_preview,
            band2_preview
        ]).astype(np.float32)

        cloud_percent, cloud_score, texture = (
           calculate_cloud_percent(
              rgb
            )
        )

        cloud_category = get_cloud_category(
            cloud_percent
        )

        p2 = np.percentile(
            rgb,
            2
        )

        p98 = np.percentile(
            rgb,
            98
        )

        rgb = np.clip(
            (rgb - p2) /
            (p98 - p2 + 1e-8),
            0,
            1
        )

        preview_filename = f"preview_{i}.jpg"

        preview_path = os.path.join(
            STATIC_FOLDER,
            preview_filename
        )

        plt.imsave(
            preview_path,
            rgb
        )
        print(
            f"Preview Saved: {time.time()-start_time:.1f}s"
        )

        scenes.append({
            "id": i,
            "date": scene_date,
            "preview": preview_filename,
            "combined": combined_path,
            "cloud_percent": round(
                cloud_percent,
                2
            ),
            "cloud_score": round(
                cloud_score,
                2
            ),
            "texture": round(
                float(texture),
                4
            ),
            "suggested_category":
                cloud_category,
            "path":
                metadata.get("Path"),
            "row":
                metadata.get("Row"),
            "scene_center_lat":
                metadata.get("SceneCenterLat"),
            "scene_center_lon":
                metadata.get("SceneCenterLon"),
            "date_of_pass":
                metadata.get("DateOfPass"),
            "product_id":
                metadata.get("ProductID"),
            "satellite":
                metadata.get("SatID"),
            "sensor":
                metadata.get("Sensor"),
            "ul_lat":
                metadata.get("ProdULLat"),
            "ul_lon":
                metadata.get("ProdULLon"),
            "ur_lat":
                metadata.get("ProdURLat"),
            "ur_lon":
                metadata.get("ProdURLon"),
            "lr_lat":
                metadata.get("ProdLRLat"),
            "lr_lon":
                metadata.get("ProdLRLon"),
            "ll_lat":
                metadata.get("ProdLLLat"),
            "ll_lon":
                metadata.get("ProdLLLon")
        })

    metadata_path = os.path.join(
        SCENE_FOLDER,
        "metadata.json"
    )
    print(
        json.dumps(
            scenes,
            indent=4
        )
    )
    with open(
        metadata_path,
        "w"
    ) as f:
        json.dump(
            scenes,
            f,
            indent=4
        )

    return render_template(
        "preview.html",
        scenes=scenes
    )

@app.route("/save", methods=["POST"])
def save_scene():

    metadata_path = os.path.join(
        SCENE_FOLDER,
        "metadata.json"
    )

    if not os.path.exists(
        metadata_path
    ):
        return "metadata.json not found."

    with open(
        metadata_path,
        "r"
    ) as f:

        scenes = json.load(f)

    saved_files = []

    metadata_db = os.path.join(
        DATASET_FOLDER,
        "dataset_metadata.json"
    )

    if os.path.exists(metadata_db):

        with open(
            metadata_db,
            "r"
        ) as f:

            dataset_metadata = json.load(f)

    else:

        dataset_metadata = []

    for scene in scenes:

        scene_id = scene["id"]

        cloud_category = request.form.get(
            f"cloud_category_{scene_id}"
        )

        clean_category = request.form.get(
            f"clean_category_{scene_id}",
            "unknown"
        )


        if not cloud_category:
            continue

        category_folder = os.path.join(
            DATASET_FOLDER,
            cloud_category
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

        while os.path.exists(destination):

            destination = os.path.join(
                category_folder,
                f"{base_name}_{counter}.tif"
            )

            counter += 1

        shutil.copy(
            scene["combined"],
            destination
        )

        saved_files.append(
            destination
        )

        date_obj = datetime.strptime(
            scene["date"],
            "%Y_%m_%d"
        )

        month = date_obj.month

        if month in [12, 1, 2]:
            season = "winter"

        elif month in [3, 4, 5]:
            season = "pre_monsoon"

        elif month in [6, 7, 8, 9]:
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

        if month in [12, 1, 2]:

            if elevation > 2500:

                snow_risk = True

        cloud_score = scene["cloud_score"]

        if snow_risk:

            cloud_score *= 0.7

        dataset_metadata.append({
            "file": os.path.basename(destination),
            "tif_path": destination.replace("\\", "/"),
            "texture": scene["texture"],
            "category": cloud_category,
            "snow_risk": snow_risk,
            "elevation": elevation,
            "cloud_score": round(
                cloud_score,
                2
            ),
            "clean_category": clean_category,
            "path": scene["path"],
            "row": scene["row"],
            "date": scene["date"],
            "year": date_obj.year,
            "month": date_obj.month,
            "season": season,
            "cloud_percent": scene["cloud_percent"],
            "scene_center_lat": scene["scene_center_lat"],
            "scene_center_lon": scene["scene_center_lon"],
            "ul_lat": scene["ul_lat"],
            "ul_lon": scene["ul_lon"],
            "ur_lat": scene["ur_lat"],
            "ur_lon": scene["ur_lon"],
            "lr_lat": scene["lr_lat"],
            "lr_lon": scene["lr_lon"],
            "ll_lat": scene["ll_lat"],
            "ll_lon": scene["ll_lon"],
            "satellite": scene["satellite"],
            "sensor": scene["sensor"],
            "product_id": scene["product_id"]
        })

    with open(
    metadata_db,
    "w"
) as f:

        json.dump(
            dataset_metadata,
            f,
            indent=4
        )

    print(
        "\nCleaning uploads/scenes..."
    )

    if os.path.exists(
        SCENE_FOLDER
    ):
 
        shutil.rmtree(
            SCENE_FOLDER
        )

    os.makedirs(
        SCENE_FOLDER,
        exist_ok=True
    )

    print(
        "uploads/scenes cleaned."
    )

    print(
        "\nRunning Pipeline...\n"
    )
    
    try:
    
        subprocess.run(
            ["python", "pipeline.py"],
    check=True
)

    except subprocess.CalledProcessError as e:
    
        print(
            f"\nPipeline Failed: {e}\n"
        )

        if os.path.exists(
            "aligned"
        ):

            shutil.rmtree(
                "aligned"
         )

        print(
            "aligned folder cleaned."
        )

        print(
            "\nPipeline Complete\n"
        )

    except subprocess.CalledProcessError as e:
    
        print(
            f"\nPipeline Failed: {e}\n"
        )
    
    html = """
    <html>
    <head>
    <title>Saved</title>
    <style>
    body{
        font-family:Arial;
        padding:40px;
        background:#f5f5f5;
    }
    
    .card{
        background:white;
        padding:30px;
        border-radius:12px;
        max-width:1000px;
        margin:auto;
        box-shadow:0px 0px 15px rgba(0,0,0,0.1);
    }

    li{
        margin-bottom:10px;
    }
    </style>
    </head>

    <body>

    <div class='card'>

    <h1>Scenes Saved Successfully</h1>

    <ul>
    """

    for file in saved_files:
        html += f"<li>{file}</li>"

    html += """

    </ul>
    
    <br>

    <a href='/'>
    Process More Scenes
    </a>

    </div>

    </body>
    </html>
    """

    return html

if __name__ == "__main__":
    app.run(
        debug=True
    )