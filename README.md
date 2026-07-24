# LISS-IV Automated Dataset Builder

by Yash Badodiya
LinkedIn= https://www.linkedin.com/in/yash-badodiya-11571b378/

## Overview

This project automatically creates a cloud removal training dataset from LISS-IV satellite imagery.

Instead of manually preparing data, the system processes multiple LISS-IV ZIP files, finds overlapping scenes, aligns them, and generates AI-ready training patches automatically.

The final dataset can be used to train deep learning models such as U-Net or Attention U-Net for cloud removal.

---

# Downloading Required Data

The dataset builder requires two types of data:

1. LISS-IV Satellite Images
2. Digital Elevation Model (DEM)

---

# 1. LISS-IV Satellite Images

# Downloading LISS-IV Satellite Data

This project uses **LISS-IV (Linear Imaging Self Scanner-IV)** optical satellite imagery from **Resourcesat-2/Resourcesat-2A**.

The Dataset Builder is designed to work directly with the original downloaded ZIP files.

---

## Download Source

LISS-IV imagery can be downloaded from the **ISRO Bhoonidhi Portal**.

Website:

https://bhoonidhi.nrsc.gov.in/

Create an account and log in.

---

## Data Selection

While searching for data, select the following:

**Data Type**

```
Optical Data
```

**Satellite**

```
Resourcesat-2
or
Resourcesat-2A
```

**Sensor**

```
LISS-IV
```

**Spatial Resolution**

```
5m-25m (medium)
```

Choose the required:

- Study Area
- Date Range
- Cloud Conditions (if available)
- Path/Row

Then add the scenes to your cart and download them as ZIP files.

---

## Supported Product

The application is designed for **LISS-IV Multi-Spectral (MX)** products.

Typical specifications:

| Property | Value |
|----------|-------|
| Satellite | Resourcesat-2 / Resourcesat-2A |
| Sensor | LISS-IV |
| Data Type | Optical |
| Spatial Resolution | 5-25 m |
| Bands Used | Band 2 (Green), Band 3 (Red), Band 4 (NIR) |
| Product Format | GeoTIFF (.tif) |
| Metadata | BAND_META.txt |

---

## Important

Do **NOT** extract the downloaded ZIP files.

The Dataset Builder automatically:

- Extracts the ZIP
- Reads the metadata
- Finds BAND2
- Finds BAND3
- Finds BAND4
- Creates the RGB image
- Estimates cloud percentage
- Generates the training dataset

Simply upload the original ZIP files using the web interface.

---

## Example ZIP Structure

```
LISS4_SCENE.zip

│
├── BAND2.tif
├── BAND3.tif
├── BAND4.tif
├── BAND_META.txt
└── ...
```

No manual extraction or renaming is required.

---

# 2. Digital Elevation Model (DEM)

Elevation data is optional but recommended.

It is used to:

- Estimate snow risk
- Improve metadata
- Future AI model improvements

Recommended source:

Copernicus DEM (30 m)

Download from:

https://dataspace.copernicus.eu/

or

OpenTopography

https://opentopography.org/

or

USGS Earth Explorer

https://earthexplorer.usgs.gov/

Download the DEM covering your study area.

Place the DEM files inside:

```
dem/
```

Example:

```
dem/

Copernicus_DEM.tif
```

The system automatically reads elevation values for every scene.

---

# Required LISS-IV Product Structure

The downloaded ZIP should contain files similar to:

```
BAND2.tif
BAND3.tif
BAND4.tif
BAND_META.txt
```

The Dataset Builder automatically detects these files.

No manual extraction or renaming is required.

---

# Storage Requirements

Large projects require significant storage.

Recommended:

| Dataset Size | Free Disk Space |
|--------------|----------------:|
| Small Project | 20 GB |
| Medium Project | 100 GB |
| Large Project | 300+ GB |

Patch datasets can become much larger than the original satellite imagery.

---

# Internet Requirements

Downloading LISS-IV imagery requires a stable internet connection.

If downloading large datasets:

- Download in batches.
- Keep original ZIP files as backup.
- Do not rename internal files inside the ZIP archives.

---

# Notes

- Only original LISS-IV ZIP files are supported.
- Do not modify the contents of the ZIP file.
- The application automatically extracts only the required files.
- Metadata is read automatically from `BAND_META.txt`.

# Pipeline

```
LISS-IV ZIP Files
        │
        ▼
Upload
        │
        ▼
Metadata Extraction
        │
        ▼
Preview Generation
        │
        ▼
Manual Verification
        │
        ▼
Dataset Save
        │
        ▼
Find Overlapping Scenes
        │
        ▼
Create Training Pairs
        │
        ▼
Image Alignment
        │
        ▼
Patch Extraction
        │
        ▼
Training Dataset
```

---

# Folder Structure

```
project/

│
├── app.py
├── pipeline.py
│
├── dataset/
├── aligned/
├── patches/
│
├── uploads/
├── static/
├── templates/
│
├── models/
│
└── README.md
```

---

# How to Use

## Step 1

Run

```bash
python app.py
```

Open

```
http://127.0.0.1:5000
```

---

## Step 2

Upload one or more extracted LISS-IV ZIP files.

The system automatically:

- extracts ZIP files
- reads metadata
- finds BAND2
- finds BAND3
- finds BAND4
- creates RGB image
- estimates cloud percentage
- creates preview

---

## Step 3

Review every scene.

You can:

- verify cloud percentage
- change cloud category
- mark scene quality
- manually mark cloud regions (optional)

---

## Step 4

Click

```
Save All Scenes
```

The system automatically:

- copies RGB TIFF into dataset
- saves metadata
- stores scene information

Then the automation pipeline starts automatically.

---

# Automatic Pipeline

After saving, the following scripts run automatically.

---

## 1. find_overlaps.py

Reads all saved metadata.

Compares every scene with every other scene.

Finds scenes covering the same location.

Output:

```
overlap_pairs.json
```

---

## 2. create_training_pairs.py

Chooses:

- cloudy image
- clearer reference image

Creates valid training pairs.

---

## 3. align_all_pairs.py

Aligns the cloudy image with the clear image.

Both images become pixel aligned.

Output:

```
aligned/

pair_001
pair_002
pair_003
...
```

Each pair contains

```
cloudy.tif
clear.tif
```

---

## 4. extract_patches.py

Reads every aligned pair.

Splits images into

```
256 × 256
```

patches.

Rejects

- empty patches
- NoData patches
- mostly black patches

Saves

```
patches/

cloudy/
clear/
```

Each cloudy patch has an identical clear patch.

Example

```
cloudy/
patch_000001.npy

clear/
patch_000001.npy
```

---

# Automatic Patch Numbering

Patch numbering is automatic.

Example

First run

```
patch_000001.npy

...

patch_050000.npy
```

Second run

```
patch_050001.npy

...

patch_080000.npy
```

Existing patches are never overwritten.

---

# Duplicate Protection

The extractor remembers which aligned pairs have already been converted into patches.

Previously processed pairs are skipped automatically.

Only new aligned pairs generate new patches.

---

# Metadata Saved

For every scene the following information is stored.

- Path
- Row
- Date
- Latitude
- Longitude
- Satellite
- Sensor
- Product ID
- Cloud Percentage
- Cloud Category
- Elevation
- Season

---

# Dataset Output

```
patches/

cloudy/

patch_000001.npy
patch_000002.npy
...

clear/

patch_000001.npy
patch_000002.npy
...
```

Every cloudy patch has exactly one matching clear patch.

---

# AI Training

The generated dataset can be used to train

- U-Net
- Attention U-Net
- Diffusion Models
- Transformer based reconstruction models

---

# Requirements

Python

Flask

Rasterio

NumPy

Matplotlib

PyTorch

GDAL (recommended)

---

# Configuration

Before running the project, update the folder paths according to your computer.

---

## 1. Dataset Folder

Open:

```
app.py
```

Find:

```python
DATASET_FOLDER = r"C:\ISRO Hackathon\dataset"
```

Replace it with the location where you want your permanent dataset to be stored.

Example:

```python
DATASET_FOLDER = r"D:\LISS_Dataset"
```

This folder stores:

```
dataset/
├── 0-10/
├── 10-20/
...
├── 90-100/
└── dataset_metadata.json
```

---

## 2. Upload Folder

In `app.py` you will find:

```python
UPLOAD_FOLDER = "uploads"
```

Normally this does not need to be changed.

It stores temporary uploaded ZIP files during processing.

---

## 3. Scene Folder

Find:

```python
SCENE_FOLDER = os.path.join(
    UPLOAD_FOLDER,
    "scenes"
)
```

Normally no changes are required.

This folder contains temporary extracted scenes.

It is automatically cleaned after successful processing.

---

## 4. Static Folder

Find:

```python
STATIC_FOLDER = "static"
```

This folder stores preview images shown on the web interface.

No changes are required.

---

## 5. DEM Folder (Elevation)

If using elevation support, place your DEM files inside:

```
dem/
```

If you move this folder, update the path inside:

```
elevation_lookup.py
```

to match the new location.

---

## 6. Models Folder

Store AI models inside:

```
models/
```

Example:

```
models/

best_model.pth
attention_unet_v2.pth
future_model.pth
```

The Cloud Removal application automatically loads models from this folder.

---

## 7. Output Folder

Generated outputs are stored inside:

```
patches/

cloudy/

clear/
```

Normally this location should not be changed.

---

## 8. Aligned Images

Temporary aligned images are stored in:

```
aligned/
```

These images are used to generate training patches.

---

## 9. Patch Size

Open:

```
extract_patches.py
```

Find:

```python
PATCH_SIZE = 256
```

Recommended value:

```
256
```

Do not change unless you also retrain the AI model with the same patch size.

---

# Directory Overview

```
Project Folder

│
├── app.py
├── pipeline.py
│
├── uploads/          (Temporary uploads)
├── static/           (Preview images)
├── dataset/          (Permanent dataset)
├── aligned/          (Aligned image pairs)
├── patches/          (Training patches)
├── models/           (AI models)
├── dem/              (Elevation data)
├── templates/        (HTML pages)
│
└── README.md
```

---

# Automatic Cleanup

The system automatically removes temporary files after processing.

Automatically cleaned:

```
uploads/scenes/
```

Not deleted:

```
dataset/
aligned/
patches/
models/
dataset_metadata.json
```

These folders contain the permanent dataset and generated training data.

---

# Before Running

Verify the following:

- Python is installed.
- Required libraries are installed.
- `DATASET_FOLDER` points to the correct location.
- DEM files (optional) are placed in the `dem/` folder.
- LISS-IV ZIP files are available.
- Enough disk space is available (recommended 100 GB or more for large datasets).

# Notes

- Only LISS-IV data is supported.
- Patch size is fixed at 256 × 256.
- Images are automatically aligned before patch extraction.
- Metadata is stored for future filtering and model improvement.
- Existing patches are preserved when new data is added.
- Previously processed image pairs are skipped automatically.

---

# Future Improvements

- Attention U-Net V2
- Automatic cloud mask generation
- Cloud mask editing tool
- Multi-model inference
- Batch prediction
- Cloud-free image reconstruction
- Web-based inference application

---

Developed for:

**Generative AI Based Cloud Removal and Reconstruction of LISS-IV Satellite Imagery**
# 👨‍💻 Author

**Yash Badodiya**

Physics Undergraduate

Central University of Jammu

LinkedIn

https://linkedin.com/in/yash-badodiya-11571b378

---

⭐ If this project helped you, consider starring the repository.
