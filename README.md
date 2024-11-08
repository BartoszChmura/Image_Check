# Image Check

## Description

**Image Check** is a tool designed to evaluate the quality of images, specifically aimed at identifying defects that may impact 3D reconstruction processes. The main purpose is to automatically detect issues such as blur, noise, distortions, overexposure and poor saturation which can hinder the accurate reconstruction of objects or scenes.
In the field of 3D modeling and reconstruction, the quality of input images is critical. Poor-quality images can lead to inaccurate models, increased processing time, and a higher failure rate in reconstruction. **Image Check** offers a comprehensive solution by analyzing images and identifying potential problems before they are used in the 3D reconstruction pipeline.

## Features

- **Automatic Image Filtering**: Automatically classifies good and bad images based on quality metrics like blur, noise, distortions, overexposure, and saturation issues.
- **Defect Detection**: Detects defects such as blur, noise, distortions, overexposure and poor saturation.
- **Silhouette Extraction**: Utilizes YOLOv8 to accurately extract silhouettes for further analysis.
- **3D Keypoint Detection**: Identifies keypoints critical for 3D reconstruction.
- **Configurable Filters**: Allows customizable threshold settings for filters/detections.

## Technologies Used

- **Python 3.14+**
- **OpenCV**
- **PyQt**
- **ultralytics YOLOv8**

## Getting Started

You can use **Image Check** in two ways: by running the pre-built `.exe` file or by cloning the project and installing the dependencies manually.

### Pre-requirements

- **Operating System**: Windows (currently the only supported OS)
- **Python Version**: Python 3.14+ (if using the manual setup)

### Option 1: Using the Pre-built `.exe` File

1. Download the latest release of `image_check.exe` from the [Releases]([https://github.com/your-repo/image-check/releases](https://github.com/BartoszChmura/Image_Check/releases/tag/v1.0)) section on GitHub.
2. Run the `.exe` file directly on your Windows machine.
3. Follow the on-screen prompts to select the images and view the results.

### Option 2: Manual Setup

If you prefer more control over the environment or want to customize the project, follow these steps:

#### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/your-repo/image-check.git
   cd image-check

2. Install the dependencies:

   ```bash
   pip install -r requirements.txt

3. Launch the Application:

    ```bash
    python main.py
    ````` 

    This command will open the Image Check GUI, where you can easily upload images, configure quality filters, and view analysis results.
   
