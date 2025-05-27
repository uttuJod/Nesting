import os
from lxml import etree


def process_svg(svg_path, rotation_angle):
    """Rotates an SVG, adds an invisible rectangle at the viewBox, and returns the modified SVG element."""

    with open(svg_path, "r") as f:
        svg_content = f.read()
    parser = etree.XMLParser(remove_blank_text=True)
    svg_layer = etree.fromstring(svg_content.encode(), parser)

    viewBox = svg_layer.get("viewBox")
    if not viewBox:
        print(f"Skipping {svg_path} - No viewBox found.")
        return None

    x_min, y_min, width, height = map(float, viewBox.split())
    cx, cy = x_min + width / 2, y_min + height / 2

    # Create a group for the rotated content
    g_rotated = etree.Element("g", transform=f"rotate({rotation_angle}, {cx}, {cy})")

    # Move original SVG elements into the rotated group
    for element in svg_layer:
        g_rotated.append(element)

    # Create a separate group for the rectangle with reverse rotation
    rect = etree.Element(
        "rect",
        x=str(x_min),
        y=str(y_min),
        width=str(width),
        height=str(height),
        fill="none",
        stroke="none",
    )

    # Create an outer container and combine both elements
    g_outer = etree.Element("g")
    g_outer.append(g_rotated)  # Add rotated elements
    g_outer.append(rect)  # Add the unrotated rectangle

    return g_outer, x_min, y_min


def assemble_svg(
    x_positions,
    y_positions,
    rotations,
    processed_svg_folder,
    output_svg_path,
    canvas_height_mm,
):
    """Places modified SVGs onto a larger canvas with transformations."""

    max_x = max(x_positions) * 4
    canvas_width_mm = max_x + 200  # Set width to max X coordinate

    svg_ns = "http://www.w3.org/2000/svg"
    root = etree.Element(
        "svg",
        xmlns=svg_ns,
        width=f"{canvas_width_mm}mm",
        height=f"{canvas_height_mm}mm",
        viewBox=f"0 0 {canvas_width_mm} {canvas_height_mm}",
    )
    print(len(rotations))
    for index in range(len(rotations)):
        x, y, theta = x_positions[index] * 4, y_positions[index] * 4, rotations[index]
        LLL = f"{index+1:03d}"  # Format filename as 001, 002, etc.

        svg_path = os.path.join(processed_svg_folder, f"{LLL}.svg")
        if not os.path.exists(svg_path):
            print(f"Skipping {LLL}.svg - File not found.")
            continue

        modified_svg, x_min, y_min = process_svg(svg_path, theta)
        if modified_svg is None:
            continue

        # Wrap in a translation group for final placement
        g_outer = etree.Element("g", transform=f"translate({x-x_min}, {y-y_min})")
        g_outer.append(modified_svg)

        root.append(g_outer)

    with open(output_svg_path, "wb") as f:
        f.write(etree.tostring(root, pretty_print=True))

    print(f"Final assembled SVG saved as: {output_svg_path}")


# Example usage:

rotations = [
    90,
    210,
    300,
    240,
    270,
    60,
    150,
    270,
    300,
    330,
    150,
    90,
    150,
    120,
    210,
    120,
    210,
    240,
]
x_positions = [
    76,
    67,
    12,
    47,
    54,
    30,
    14,
    29,
    31,
    46,
    0,
    1,
    76,
    3,
    25,
    19,
    45,
    1,
    36,
    75,
    84,
    58,
    16,
    10,
    56,
]
y_positions = [
    65,
    5,
    20,
    24,
    59,
    37,
    62,
    59,
    3,
    69,
    6,
    48,
    23,
    29,
    75,
    5,
    46,
    78,
    6,
    62,
    70,
    59,
    59,
    66,
    69,
]


processed_svg_folder = "output_svgs"
output_svg_path = "final_assembled.svg"
canvas_height_mm = 400

assemble_svg(
    x_positions,
    y_positions,
    rotations,
    processed_svg_folder,
    output_svg_path,
    canvas_height_mm,
)
