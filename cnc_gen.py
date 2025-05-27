import os

# Sample input arrays
"""y_positions = [
    311,
    20,
    287,
    167,
    157,
    221,
    192,
    17,
    5,
    207,
    325,
    296,
    0,
    91,
    221,
    157,
    9,
    25,
    166,
    320,
    68,
    1,
    271,
    124,
    262,
    119,
    275,
    8,
    158,
    72,
]
x_positions = [
    243,
    909,
    635,
    241,
    834,
    152,
    721,
    551,
    65,
    592,
    89,
    456,
    672,
    687,
    2,
    421,
    333,
    443,
    500,
    889,
    236,
    172,
    994,
    593,
    356,
    981,
    782,
    811,
    90,
    3,
]  # Y coordinates
rotations = [
    90,
    90,
    270,
    180,
    180,
    270,
    45,
    45,
    90,
    0,
    0,
    315,
    135,
    135,
    225,
    45,
    90,
    90,
    90,
    180,
    315,
    90,
    90,
    45,
    270,
    315,
    180,
    45,
    90,
    270,
]
"""
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
canvas_width = max(x_positions)  # Equivalent to (canvas.cols + 100)
canvas_height = 400  # Fixed height
y_corr = 9.00

# NC output file
nc_filename = "output.nc"

# Constants
zHeight = 80  # Initial Z height
z1Height = 95  # Initial Z height
layerThickness = 0.08  # Z increment per placement

# Center offsets


# Generate NC code
def generate_nc_code(nc_filename, x_positions, y_positions, rotations):
    with open(nc_filename, "w") as nc_file:
        # Write header
        nc_file.write("%00001\n")
        nc_file.write("N10 G21\n")
        nc_file.write("Z85\n")

        lineNumber = 20
        xPrev = 0
        global zHeight, z1Height

        for index in range(len(rotations)):
            x = x_positions[index]
            y = y_positions[index] + 10

            print(
                f"Processing layer {index+1}: x={x}, y={y-200-y_corr}, angle={rotations[index]}"  # -200 is because laser 0,0 is at centerline of paper, while svg 0,0 is at top left.
                # further correction factor of +50, taken from previous code
            )

            # Write NC commands
            nc_file.write(f"N{index+1}{lineNumber} G91\n")
            lineNumber += 10
            nc_file.write(f"N{index+1}{lineNumber} A{x - xPrev} B{x - xPrev}\n")
            lineNumber += 10
            nc_file.write(f"N{index+1}{lineNumber} G90\n")
            lineNumber += 10
            nc_file.write(f"N{index+1}{lineNumber} Y{y-200-y_corr}\n")
            lineNumber += 10
            nc_file.write(f"N{index+1}{lineNumber} C{rotations[index]}\n")
            lineNumber += 10
            nc_file.write(f"N{index+1}{lineNumber} Z{zHeight}\n")
            lineNumber += 10
            nc_file.write(f"N{index+1}{lineNumber} G04 X40\n")
            lineNumber += 10
            nc_file.write(f"N{index+1}{lineNumber} Z{z1Height}\n")
            lineNumber += 10

            # Update Z heights
            zHeight += layerThickness
            z1Height += layerThickness
            xPrev = x

        # Final movement
        nc_file.write(f"N{lineNumber} G91\n")
        lineNumber += 10
        nc_file.write(f"N{lineNumber} A{(canvas_width)} B{(canvas_width )}\n")
        lineNumber += 10

    print(f"NC code saved to {nc_filename}")


# Run the function
generate_nc_code(nc_filename, x_positions, y_positions, rotations)
