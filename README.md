# Ajust-Image-Converter
<!-- Python (3.10.4) -->
![Python](https://img.shields.io/badge/language-Python-3776AB?style=flat-square&logo=python&logoColor=white)
![version](https://img.shields.io/badge/version-3.10.4-3776AB?style=flat-square&logo=python&logoColor=white)

<img width="600" height="410" alt="github_0" src="https://github.com/user-attachments/assets/f4f263bb-ded5-4b4f-913c-2fae527b0dff" />

## Download
<a href="https://github.com/Sadc2h4/Ajust-Image-Converter/releases/tag/V1.0a">
  <img
    src="https://raw.githubusercontent.com/Sadc2h4/brand-assets/main/button/Download_Button_1.png"
    alt="Download .zip"
    height="48"
  />
</a>
<br>
<a href="https://www.dropbox.com/scl/fi/cguqt5sppbx231t4cm961/Ajust-Image-Converter.zip?rlkey=r7d0n6e5fljcepq7mb2njmgan&st=oqsddfgy&dl=1">
  <img
    src="https://raw.githubusercontent.com/Sadc2h4/brand-assets/main/button/Download_Button_4.png"
    alt="Download .zip"
    height="48"
  />
</a>
<br>

## Features
A simple GUI tool that batch-converts images in a selected folder to PNG, saving results into a time-stamped output folder.  
Optional one-click operations include left–right mirroring, pixel-art friendly ×4 upscaling (nearest-neighbor),   
aspect-ratio-preserving canvas resize, and background removal (rembg).  
Workflow is intentionally minimal: choose a folder → start conversion.　  

Using this tool's image conversion can improve the accuracy of Lora creation to a certain extent.


# Feasible functions

## Batch convert to PNG & sequential renaming  
 Saves as 
 ```01_<your-name>.png, 02_<your-name>.png, …```  
 If no name is provided, convert_ is used.
 Output folder name is ```YYYY.MM.DD.HHMMSS_convert```.  

## ptional left–right mirror  
 Generates an additional _mirrored image.  

## Pixel-art ×4 upscale (nearest-neighbor)  
 Preserves crisp edges; works with alpha images.  

## Auto canvas resize with aspect ratio preserved  
 >Expands canvas and centers the image on white background to one of:  
 ・1024 × 1024 (near-square)  
 ・1216 × 832 (landscape; width ≥ height + 200)  
 ・832 × 1216 (portrait; height ≥ width + 200)  

## Background removal (optional, via rembg)  
 Saves results into the removeBG subfolder.  
 First use may take longer due to model warm-up.  

## Progress & status bars  
 Shows conversion progress and the selected folder path.  

# Installation / Run  
A) Run with Python  
(Recommended) Create and activate a virtual environment.  

Install dependencies:  
```pip install pillow pyqt5 rembg```  

Launch:
```python png_changer.py```  

Launch the app (png_changer.py or the packaged .exe).

## Usage

https://github.com/user-attachments/assets/13dea233-3f77-4a65-a014-36668e92cd9d

1. Launch the app (`png_changer.py` or the packaged `.exe`).
2. Click **Select the folder to be converted** and choose the target folder.
3. *(Optional)* Enter a common filename stem (the part after the sequence number).
4. Toggle options as needed:
   - [ ] **Create left-to-right flipped image**
   - [ ] **Automatic image size conversion**
   - [ ] **Sharpen enlarged images** (pixel-art ×4)
   - [ ] **Background removed** (rembg)
5. Click **Start Conversion**.
6. When using background removal, the initial loading may take about one minute.

https://github.com/user-attachments/assets/8c54a68f-87ba-453c-bfe4-c5378b5df7cf

### Output
- Converted PNGs are saved into `YYYY.MM.DD.HHMMSS_convert/`.
- If background removal is enabled, removed-background PNGs are stored under `removeBG/`.

## Deletion Method
・Please delete the entire file.

## Disclaimer
・I assume no responsibility whatsoever for any damages incurred through the use of this file.
B) Run as a standalone EXE
Use a prebuilt .exe if provided, or build your own with PyInstaller (see Build Notes).  
Note: Background removal loads rembg/ONNX models on first use, so initial runs with that option enabled may take longer.  

