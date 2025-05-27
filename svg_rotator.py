import os
import io
import math
import cairosvg
from PIL import Image
from lxml import etree
import re
import copy
import cv2
import numpy as np


def normalize_svg_canvas(svg_path):
    """Expands the smaller dimension of the SVG to match the larger one while centering the shape."""

    # Load and parse the SVG file
    with open(svg_path, "r") as f:
        svg_content = f.read()

    parser = etree.XMLParser(remove_blank_text=True)
    root = etree.fromstring(svg_content.encode(), parser)

    # Extract the viewBox if it exists, otherwise set default values
    viewBox = root.get("viewBox")
    if viewBox:
        x_min, y_min, width, height = map(float, viewBox.split())
    else:
        width = float(root.get("width", 100))
        height = float(root.get("height", 100))
        x_min, y_min = 0, 0
        root.set("viewBox", f"{x_min} {y_min} {width} {height}")

    # Compute center
    cx = x_min + width / 2
    cy = y_min + height / 2

    # Compute new side length to fit rotation
    diagonal = math.sqrt(width**2 + height**2) + 15

    # Compute new min_x and min_y to keep center fixed
    new_x_min = cx - diagonal / 2
    new_y_min = cy - diagonal / 2

    # Update viewBox
    root.set("viewBox", f"{new_x_min} {new_y_min} {diagonal} {diagonal}")

    root.set("width", str(diagonal))
    root.set("height", str(diagonal))

    # Add a White Background Rectangle
    """bg_rect = etree.Element(
        "rect",
        x=str(new_x_min),
        y=str(new_y_min),
        width=str(diagonal),
        height=str(diagonal),
        fill="none",
        stroke="none",
    )
    root.insert(0, bg_rect)  # Insert as the first element"""

    return root, new_x_min, new_y_min, diagonal  # Return updated SVG and parameters


def rotate_and_convert_to_bmp(
    svg_path, output_svgs_folder, output_bmps_folder, angle_step=30, scale=0.25
):
    """Rotates the SVG in steps and outputs a BMP for each rotated version."""

    os.makedirs(output_svgs_folder, exist_ok=True)
    os.makedirs(output_bmps_folder, exist_ok=True)

    # Extract layer number (LLL) from filename using regex
    match = re.search(r"(\d{3})\.svg$", svg_path)
    if not match:
        print(f"Skipping file {svg_path}: Could not extract layer number.")
        return
    LLL = match.group(1)  # Extracted layer number (e.g., "001")

    # Normalize SVG
    root, x_min, y_min, max_dim = normalize_svg_canvas(svg_path)

    # **Save the processed (viewBox-adjusted) SVG**
    normalized_svg_path = os.path.join(output_svgs_folder, f"{LLL}.svg")
    with open(normalized_svg_path, "wb") as f:
        f.write(etree.tostring(root, pretty_print=True))
    print(f"Saved normalized SVG: {normalized_svg_path}")

    # Define center for rotation
    cx, cy = x_min + (max_dim / 2), y_min + (max_dim / 2)

    # Define the SVG namespace
    ns = {"svg": "http://www.w3.org/2000/svg"}

    # Find all polygons
    polygons = root.findall(".//svg:polygon", namespaces=ns)
    if not polygons:
        print(f"Skipping file {svg_path}: No polygons found.")
        return

    for angle in range(0, 360, angle_step):
        rotated_root = copy.deepcopy(root)  # Fresh copy for this rotation
        rotated_polygons = rotated_root.findall(".//svg:polygon", namespaces=ns)

        for polygon in rotated_polygons:
            polygon.set("transform", f"rotate({angle}, {cx}, {cy})")

            # Modify Existing Style Attribute
            style = polygon.get("style", "")
            if "fill:none" in style:
                style = style.replace("fill:none", "fill:black")
            else:
                style += ";fill:black"
            polygon.set("style", style.strip())

        # Convert rotated_root to PNG
        svg_bytes = etree.tostring(rotated_root, pretty_print=True)
        png_data = cairosvg.svg2png(bytestring=svg_bytes, scale=scale)

        # Convert to strictly black-and-white BMP
        img = Image.open(io.BytesIO(png_data)).convert("L")

        # Adjust Threshold for Better Contour Isolation
        bw = img.point(lambda p: 255 if p < 200 else 0, "1")  # black/white separation

        # -----> START DILATION STEP
        bw_np = np.array(bw, dtype=np.uint8) * 255  # convert back to 0-255
        kernel = np.ones((3, 3), np.uint8)  # 3x3 square structuring element
        dilated = cv2.dilate(bw_np, kernel, iterations=1)
        dilated = cv2.bitwise_not(dilated)
        dilated_img = Image.fromarray(dilated).convert(
            "1"
        )  # back to Pillow Image (mode "1")
        # -----> END DILATION STEP

        # Define Output BMP Filename
        bmp_filename = f"{LLL}_00_{angle:03d}.bmp"
        bmp_path = os.path.join(output_bmps_folder, bmp_filename)

        # Save BMP
        dilated_img.save(bmp_path, "BMP")
        print(f"Saved BMP: {bmp_path}")

    print(f"Processed {360 // angle_step} images for {svg_path}")


def batch_process_svgs(
    input_folder, output_svgs_folder, output_bmps_folder, angle_step=30, scale=0.25
):
    """Processes all SVG files in the input folder."""

    # Ensure output folders exist
    os.makedirs(output_svgs_folder, exist_ok=True)
    os.makedirs(output_bmps_folder, exist_ok=True)

    # Process all SVG files
    for filename in sorted(os.listdir(input_folder)):
        if filename.endswith(".svg"):
            svg_path = os.path.join(input_folder, filename)
            rotate_and_convert_to_bmp(
                svg_path, output_svgs_folder, output_bmps_folder, angle_step, scale
            )


# Example usage: Process all SVGs in "input_svgs" folder and save processed SVGs and BMPs
angle_step = 30
scale = 0.25
batch_process_svgs("input_svgs", "output_svgs", "output_bmps", angle_step, scale)
