# Shape Detector

A Python application that detects geometric shapes (circles, rectangles, and triangles) in real-time using your webcam or from uploaded images.

![Shape Detector Demo](docs/demo.png)

## Features

- 📷 Real-time shape detection using webcam
- 📁 Upload and analyze images
- 🔵 Circle detection
- 🟦 Rectangle detection
- 🔺 Triangle detection
- 📊 Real-time statistics of detected shapes
- 🎨 Modern Qt-based user interface

## Requirements

- Python 3.6+
- OpenCV
- PyQt5
- NumPy

## Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/shape-detector.git
cd shape-detector
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the application:
```bash
python shape_detector.py
```

### Controls

- Click "📁 Charger une Image" to load an image file
- Click "📷 Activer/Désactiver Caméra" to toggle webcam
- Use checkboxes to select which shapes to detect:
  - 🔵 Circles
  - 🟦 Rectangles
  - 🔺 Triangles
- Click "🔄 Retraiter l'Image" to reprocess the current image

## How it Works

The application uses various computer vision techniques through OpenCV:
- Circle detection using Hough Circle Transform
- Rectangle and triangle detection using contour detection and polygon approximation
- Real-time image processing and shape highlighting
- Dynamic UI updates with detection statistics

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. 