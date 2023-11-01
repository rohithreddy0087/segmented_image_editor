# PyQt5 Image Segmentation and Drawing App - Dual Version

## Introduction

This branch has a updated application where we can edit two different images at the same time.

![Screenshot from 2023-10-31 18-59-15](https://github.com/rohithreddy0087/segmented_image_editor/assets/51110057/c37da16f-8952-44a0-9760-02eda8c640c8)


## Installation

Before you begin, ensure you have the necessary Python packages installed. You can install them using `pip`:

```bash
pip3 install -r requirements.txt
```

## Usage

### Getting Started

To launch the application, run `app.py`:

```bash
python3 app.py
```

Upon starting the app, you will see a canvas where you can load and manipulate images.

### Segmented Image

1. **Load Segmented Image**: Click on the "Load Image" button to load a segmented image. The app will display the segmented objects based on their colors.

2. **Move Segmented Objects**: Select and drag segmented objects with the mouse.

3. **Remove and Replace**: To remove a segmented object, click on it, and then press the "Delete" key. To replace it with a white pixel, press the "Space" key.

### Freehand Drawing

1. **Choose Drawing Color**: Select a color from the color palette displayed on the left side of the canvas.

2. **Draw Freely**: Click and drag the mouse to draw on the canvas.

### Saving the Image

To save your annotated image:

1. Click the "Save" button.
2. It will be saved with _edited.png format

## Dependencies

This application depends on the following Python packages:

- PyQt5: A set of Python bindings for the Qt application framework.
- OpenCV (headless): Open Source Computer Vision Library, used for image manipulation.
- NumPy: A fundamental package for scientific computing with Python.
- scikit-image: A collection of algorithms for image processing.
- Matplotlib: A plotting library used for displaying images and drawing.

Make sure to have these packages installed as described in the installation section.
