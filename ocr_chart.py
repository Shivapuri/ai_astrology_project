import os
from PIL import Image
import subprocess

# Open the image
img = Image.open('/Users/hajnaljanos/.gemini/antigravity-cli/brain/3f7bae9f-e552-419e-85f0-8d614728ab30/.user_uploaded/uploaded_media_1787306428918.png')

# The main South Indian chart is at the top left. Let's try to find it.
# We will just run tesseract on the whole image and search for the specific text.
# Actually, the user says "Eight and nine and the eight stars".

# Let's crop the top-left area which is the D1 chart.
# Estimate size: 800x800 around top left
cropped = img.crop((300, 100, 1000, 700))
cropped.save("temp_chart.png")

# Run tesseract
result = subprocess.run(['tesseract', 'temp_chart.png', 'stdout'], capture_output=True, text=True)
print("OCR Output:")
print(result.stdout)
