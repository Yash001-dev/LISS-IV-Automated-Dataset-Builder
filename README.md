# LISS-IV-Automated-Dataset-Builder
Automated dataset generation pipeline for LISS-IV satellite imagery with metadata extraction, cloud estimation, scene matching, alignment and AI-ready patch generation for cloud removal research.

# 🌍 LISS-IV Automated Dataset Builder

> Fully automated pipeline for generating AI-ready cloud removal datasets from ISRO LISS-IV satellite imagery.

![Python](https://img.shields.io/badge/Python-3.10-blue)
![PyTorch](https://img.shields.io/badge/PyTorch-DeepLearning-red)
![Flask](https://img.shields.io/badge/Flask-WebApp-black)
![Rasterio](https://img.shields.io/badge/Rasterio-GIS-green)

---

## 🚀 Overview

Preparing datasets for satellite cloud removal normally requires significant manual work such as downloading imagery, extracting metadata, pairing scenes, image alignment, and generating training patches.

This project automates the complete workflow for **Resourcesat-2/Resourcesat-2A LISS-IV** imagery.

Starting from raw satellite ZIP files, the pipeline automatically generates AI-ready training data suitable for deep learning models such as U-Net and Attention U-Net.

---

# ✨ Key Features

- Automatic LISS-IV ZIP extraction
- RGB image generation
- Metadata extraction
- Cloud percentage estimation
- DEM-based elevation lookup
- Snow risk estimation
- Season-aware scene matching
- Geographic overlap detection
- Automatic cloudy-clear pair generation
- Pixel alignment
- 256×256 patch extraction
- Duplicate protection
- Incremental dataset generation
- Automatic metadata storage

---

## Requirements

- Python 3.12+
- Flask 3.1.3
- PyTorch 2.12.1
- Rasterio 1.5.0
- NumPy 2.5.1
- Matplotlib 3.11.1
- Shapely 2.1.2

---

# 📂 Repository Structure

```
LISS-IV-Automated-Dataset-Builder

│
├── app.py                      # Flask web application
├── pipeline.py                 # Pipeline controller
├── find_overlaps.py            # Geographic overlap detection
├── create_training_pairs.py    # Cloudy-clear scene pairing
├── align_all_pairs.py          # Image registration
├── extract_patches.py          # Patch extraction
├── elevation_lookup.py         # DEM elevation lookup
├── model.py
│
├── uploads/
├── dataset/
├── aligned/
├── patches/
├── dem/
├── models/
├── static/
├── templates/
└── README.md
```



# 🛰 Required Data

This project requires **two datasets**.

## 1️⃣ LISS-IV Satellite Images

Download from:

https://bhoonidhi.nrsc.gov.in/

Supported:

- Resourcesat-2
- Resourcesat-2A
- LISS-IV (MX)

Required files inside every ZIP

```
BAND2.tif
BAND3.tif
BAND4.tif
BAND_META.txt
```

⚠️ Do **NOT** extract the ZIP.

Simply upload the original ZIP.

---

## 2️⃣ Digital Elevation Model (DEM)

Elevation data is **required** for the complete preprocessing pipeline.

It is used for:

- Elevation extraction
- Terrain analysis
- Snow risk estimation
- Metadata enhancement
- Scene matching

Recommended sources

- Copernicus DEM (30 m)
- OpenTopography
- USGS Earth Explorer

Place the DEM inside

```
dem/

Copernicus_DEM.tif
```

---

# ⚙ Pipeline

```
Raw LISS-IV ZIP Files
        │
        ▼
ZIP Extraction
        │
        ▼
Metadata Extraction
        │
        ▼
RGB Generation
        │
        ▼
Cloud Estimation
        │
        ▼
DEM Elevation Lookup
        │
        ▼
Snow Risk Detection
        │
        ▼
Season Matching
        │
        ▼
Geographic Overlap Detection
        │
        ▼
Training Pair Generation
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

# 📊 Dataset Statistics

Successfully tested on multi-season LISS-IV imagery.

| Metric | Value |
|---------|------:|
| Training Pairs | 146,742 |
| Generated Patches | 293,484 |
| Patch Size | 256 × 256 |
| Training Patches | 132,067 |
| Validation Patches | 14,675 |

---

# 🚀 Installation

```bash
git clone https://github.com/Yash001-dev/LISS-IV-Automated-Dataset-Builder.git

cd LISS-IV-Automated-Dataset-Builder
```

Install

```bash
pip install -r requirements.txt
```

Run

```bash
python app.py
```

Open

```
http://127.0.0.1:5000 (local host)
```

---

# 🧠 Technologies

### Programming

- Python
- Flask

### Deep Learning

- PyTorch
- NumPy

### Remote Sensing

- Rasterio
- GDAL
- GeoTIFF
- SRTM DEM

---

# 📈 Output

```
patches/

cloudy/

patch_000001.npy

clear/

patch_000001.npy
```

Every cloudy patch has one matching cloud-free patch.

---

# 🔮 Future Work

- Diffusion Models
- Transformer Reconstruction
- Sentinel-1 SAR Integration
- Sentinel-2 Guidance
- Automatic Cloud Mask Generation
- Near Real-Time Processing

---

# 👨‍💻 Author

**Yash Badodiya**

Physics Undergraduate

Central University of Jammu

LinkedIn

https://linkedin.com/in/yash-badodiya-11571b378

---

⭐ If this project helped you, consider starring the repository.
