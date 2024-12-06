# 📽️ Video to Slides Converter: Intelligent Frame Extraction

## 🚀 Project Overview

Video to Slides Converter is a powerful Python application that transforms lengthy videos into concise, meaningful slides with advanced analysis capabilities. Designed for professionals in education, business, and research, this tool helps extract key frames from videos, perform OCR, and generate comprehensive reports.

## ✨ Key Features

- **Multiple Extraction Methods**
  - KNN (K-Nearest Neighbors) Background Subtraction
  - GMG Background Subtraction
  - Frame Difference Analysis

- **Advanced Image Processing**
  - Automatic slide extraction
  - Duplicate slide removal
  - Customizable extraction parameters

- **Text Recognition**
  - Built-in Optical Character Recognition (OCR) (i used tesseract to show functionality, but you can replace it with better OCR for more accuracy)
  - Extract and save text from video frames
  - Generate text summary alongside images

- **Comprehensive Reporting**
  - JSON summary of extracted slides
  - PDF analysis report
  - Timestamp tracking for each slide

## 🛠️ Prerequisites

Before you begin, ensure you have the following installed:

- Python 3.8+
- OpenCV
- Tesseract OCR
- Required Python libraries (see `requirements.txt`)

## 📦 Installation

1. Clone the repository:
```bash
git clone https://github.com/VaibhavSharma1620//video-to-slides-converter.git
cd video-to-slides-converter
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

3. Install Tesseract OCR:
- Windows: Download from [Tesseract GitHub](https://github.com/UB-Mannheim/tesseract/wiki)
- macOS: `brew install tesseract`
- Linux: `sudo apt-get install tesseract-ocr`

## 🖥️ Usage Guide

### GUI Mode

1. Launch the application:
```bash
python video_to_slides.py
```

2. Select Input Options:
   - **Video Input**: Choose your source video
   - **Output Directory**: Select where slides will be saved

3. Configure Processing Options:
   - **Extraction Method**:
     - KNN: Best for videos with clear background changes
     - GMG: Suitable for complex scene transitions
     - Frame Diff: Ideal for detecting significant frame variations

   - **Additional Options**:
     - Remove Duplicates: Eliminate redundant slides
     - Convert to PDF: Generate a PDF of extracted slides
     - Generate Report: Create a detailed analysis document
     - OCR: Extract text from slides

### Customization

You can modify extraction parameters in the `VideoProcessor` class:
- `FRAME_BUFFER_HISTORY`: Number of frames for background modeling
- `DEC_THRESH`: Decision threshold for background subtraction
- `MIN_PERCENT`: Minimum change percentage to trigger slide extraction

## 🔍 Deep Dive: Frame Extraction Techniques

### Unraveling Frame Extraction: A Comprehensive Guide to Video Frame Selection Techniques

#### Introduction

In the realm of video processing, extracting meaningful frames is akin to finding diamonds in a mine. Not every frame holds significance, and the art of intelligent frame selection can transform hours of video into concise, informative snippets.

#### 1. K-Nearest Neighbors (KNN) Background Subtraction

##### Theoretical Foundation
KNN Background Subtraction is a sophisticated pixel-level change detection algorithm that leverages statistical learning principles. At its core, it maintains a dynamic model of the background, constantly updating and adapting to scene variations.

##### Mathematical Mechanics

**Key Parameters:**
- `history`: Number of frames used to create background model
- `dist2Threshold`: Pixel distance threshold for classification
- `detectShadows`: Shadow detection toggle

**Algorithmic Workflow:**
1. **Background Model Construction**
   The algorithm maintains a collection of recent pixel values for each pixel location.
   
   Mathematically, for each pixel (x,y):
   ```
   Background_Model(x,y) = {p1, p2, p3, ..., pn}
   Where n = history parameter
   ```

2. **Pixel Classification**
   A pixel is classified as foreground or background by comparing its current value to the background model.

   Classification Formula:
   ```
   D(pixel) = |current_value - background_value|
   If D(pixel) > dist2Threshold: Foreground
   Else: Background
   ```

3. **Adaptive Learning**
   The background model dynamically updates, giving more weight to recent observations.

   Update Rule:
   ```
   Background_Model(new) = α * current_pixel + (1-α) * Background_Model(old)
   Where α is a learning rate (typically small)
   ```

#### 2. Gaussian Mixture Model (GMG) Background Subtraction

##### Theoretical Underpinnings
GMG represents each pixel's color as a mixture of Gaussian distributions, providing a more sophisticated background modeling approach.

##### Mathematical Framework

**Core Concept:**
Represent pixel values as a weighted sum of multiple Gaussian distributions.

**Probability Density Function:**
```
P(x) = Σ(wi * N(μi, σi))
Where:
- wi: Weight of Gaussian component
- μi: Mean of the distribution
- σi: Standard deviation
- N(): Normal distribution function
```

**Key Algorithmic Steps:**
1. Initialize Gaussian components for each pixel
2. Classify incoming pixels against existing distributions
3. Update distribution parameters adaptively

#### 3. Frame Difference Analysis

##### Conceptual Overview
Frame Difference Analysis compares consecutive frames to detect significant changes, focusing on pixel-level intensity variations.

##### Mathematical Approach

**Change Detection Formula:**
```
Difference(frame_t, frame_t-1) = |Pixel(frame_t) - Pixel(frame_t-1)|
```

**Preprocessing Steps:**
1. Convert frames to grayscale
2. Apply absolute difference
3. Use thresholding to highlight significant changes

#### Structural Similarity Index (SSIM): The Duplicate Detector

##### Purpose
SSIM measures the perceptual difference between two images, crucial for removing redundant frames.

##### Mathematical Calculation
```
SSIM(x, y) = [l(x,y)]^α * [c(x,y)]^β * [s(x,y)]^γ

Where:
- l(): Luminance comparison
- c(): Contrast comparison
- s(): Structure comparison
- α, β, γ: Tunable parameters
```

**Interpretation:**
- SSIM ≈ 1: Images are nearly identical
- SSIM < 0.98: Significant differences exist

## 💡 Practical Implications

### When to Use Each Method:

1. **KNN**
   - Suitable for: Stable camera, minimal lighting changes
   - Strengths: Fast, adaptable, low computational cost

2. **GMG**
   - Suitable for: Complex backgrounds, varying lighting
   - Strengths: Robust to shadows, handles multi-modal backgrounds

3. **Frame Difference**
   - Suitable for: Detecting abrupt changes
   - Strengths: Simple, computationally lightweight

## 🔍 Example Scenarios

1. **Lecture Recording Analysis**
   - Extract key slides from long educational videos
   - Capture important visual information and text

2. **Business Presentation Summarization**
   - Generate concise slide decks from lengthy meetings
   - Track important timestamp references

3. **Research Documentation**
   - Extract visual data from experimental or observational videos
   - Perform text extraction for further analysis

## 🤝 Contributing

Contributions are welcome! Please follow these steps:
1. Fork the repository
2. Create your feature branch (`git checkout -b feature/addfeat`)
3. Commit your changes (`git commit -m 'Add some addfeat'`)
4. Push to the branch (`git push origin feature/addfeat`)
5. Open a Pull Request


## 📧 Contact

Your Name - vaibhav16204648@example.com

Project Link: [https://github.com/VaibhavSharma1620//video-to-slides-converter](https://github.com/VaibhavSharma1620//video-to-slides-converter)

## 🎬 Conclusion

Frame extraction is both an art and a science. By understanding these sophisticated techniques, we transform raw video into meaningful insights, bridging the gap between information overload and structured knowledge.

*Keep innovating, keep extracting!* 📽️🔍


## 📧 Reference and inspiration:
https://learnopencv.com/video-to-slides-converter-using-background-subtraction/
