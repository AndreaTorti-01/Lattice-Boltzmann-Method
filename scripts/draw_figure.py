import numpy as np
from PIL import Image
import sys

# Parse input data
if len(sys.argv) < 2:
    print("Usage: python draw_figure.py <input_filename>")
    sys.exit(1)

input_filename = sys.argv[1]
with open(input_filename, 'r') as f:
    lines = f.readlines()

# Parse dimensions from second line
dimensions = lines[1].strip().split()
n, m = int(dimensions[0]), int(dimensions[1])

# Create a white canvas
canvas = np.ones((m, n, 3), dtype=np.uint8) * 255

# Parse pixel coordinates starting from the fourth line
for i in range(3, len(lines)):
    line = lines[i].strip()
    if line:
        x, y = map(int, line.split())
        # Draw black pixel at (x, y)
        # Note: Image coordinates are (y, x) in numpy arrays
        if 0 <= x < n and 0 <= y < m:
            canvas[y, x] = [0, 0, 0]

# Create and save the image
img = Image.fromarray(canvas)
img.save('output.png')
print(f"Image created with dimensions {n}x{m} and saved as 'output.png'")