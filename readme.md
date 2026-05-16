# CardioScan AI — ECG Heart Disease Detector

> **An AI-powered web application for detecting cardiac abnormalities from ECG images using Deep Learning.**

[[Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://heart-disease-analysis-shlb3ucjxrhohr7dnzm5wj.streamlit.app/)
[![Python 3.11](https://img.shields.io/badge/Python-3.11-blue)](https://python.org)
[![TensorFlow 2.18](https://img.shields.io/badge/TensorFlow-2.18-orange)](https://tensorflow.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-green)](LICENSE)

---

## Project Overview

CardioScan AI is a machine learning solution for **early detection of heart disease** through automated analysis of Electrocardiogram (ECG) images. The system leverages a custom **Convolutional Neural Network (CNN)** trained to classify ECG waveform images as either **Normal** or **Diseased**.

Heart disease remains the **leading cause of death globally**. Early and accurate ECG interpretation traditionally requires trained cardiologists — this project makes preliminary screening faster and more accessible through AI.

---

## Features

| Feature | Description |
|---|---|
| **CNN Model** | Custom-built deep learning model trained on ECG images |
| **Confidence Gauge** | Visual needle-dial showing prediction confidence % |
| **Pulse Animation** | Animated result card — slow for normal, fast for disease |
| **PDF Report** | Downloadable analysis report with timestamp |
| **Scan History** | Last 5 scans tracked in the sidebar |
| **Health Tips** | Personalized tips based on prediction result |
| **Web Deployed** | Live on Streamlit Cloud — no installation needed |

---

## Model Architecture

```
Input Image (224 × 224 × 3)
        ↓
Conv2D(16, 3×3) → ReLU → MaxPooling(2×2)
        ↓
Conv2D(32, 3×3) → ReLU → MaxPooling(2×2)
        ↓
Conv2D(64, 3×3) → ReLU → MaxPooling(2×2)
        ↓
Flatten
        ↓
Dense(64) → ReLU
        ↓
Dropout(0.4)
        ↓
Dense(1) → Sigmoid
        ↓
Output: Probability [0, 1]
(< 0.5 = Disease | > 0.5 = Normal)
```

---

##  Project Structure

```
heart_disease_analysis/
├── app.py                      # Streamlit web application
├── predict_utils.py            # Model loading & inference
├── train.py                    # Model training script
├── heart_disease_model.tflite  # Trained TFLite model
├── requirements.txt            # Python dependencies
├── .gitignore                  # Git ignore rules
├── .python-version             # Python version pin (3.11)
└── ecg_data/                   # Dataset (not tracked in git)
    ├── train/
    │   ├── Normal/
    │   └── Disease/
    └── test/
        ├── Normal/
        └── Disease/
```

---

## Dataset

| Property | Details |
|---|---|
| **Source** | [Kaggle ECG Analysis Dataset](https://www.kaggle.com/datasets/evilspirit05/ecg-analysis) |
| **Type** | 2D ECG waveform images (JPG) |
| **Classes** | Normal, Disease |
| **Total Images** | ~928 |
| **Split** | Train / Test |

---

## Training Results

| Metric | Value |
|---|---|
| Optimizer | Adam |
| Loss Function | Binary Crossentropy |
| Epochs | 10 |
| Batch Size | 32 |
| Input Size | 224 × 224 px |
| **Validation Accuracy** | **~90%** |

---

## Tech Stack

| Technology | Purpose |
|---|---|
| **Python 3.11** | Core programming language |
| **TensorFlow 2.18 / Keras** | Model training & inference |
| **TFLite** | Lightweight model format for deployment |
| **Streamlit** | Web application framework |
| **PIL (Pillow)** | Image preprocessing |
| **NumPy** | Numerical operations |
| **ReportLab** | PDF report generation |
| **GitHub** | Version control & CI |
| **Streamlit Cloud** | Free cloud deployment |

---

## Installation & Setup

### Clone the Repository
```bash
git clone https://github.com/fatimasabir987/Heart-Disease-Analysis.git
cd Heart-Disease-Analysis
```

### Create Virtual Environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Run Locally
```bash
streamlit run app.py
```

---

## Model Training

To retrain the model with your own data:

```bash
# Place your data in ecg_data/train/ and ecg_data/test/
# with subfolders: Normal/ and Disease/

py -3.11 train.py
```

This generates a new `heart_disease_model.tflite` file.

---

## How to Use

1. Open the [live app](https://heart-disease-analysis-shlb3ucjxrhohr7dnzm5wj.streamlit.app/)
2. Upload an ECG image (JPG/PNG)
3. View the prediction result with confidence score
4. Download the PDF report
5. Read personalized health tips

---

## Disclaimer

> This application is developed **for research and educational purposes only**.
> It is **NOT a medical device** and should **NOT** be used as a substitute for professional medical advice, diagnosis, or treatment.
> Always consult a qualified cardiologist or physician for proper cardiac evaluation.

---

## Author

**Hafiza Fatima Sabir**
- GitHub: [@fatimasabir987](https://github.com/fatimasabir987)

---

##  License

This project is licensed under the MIT License.
