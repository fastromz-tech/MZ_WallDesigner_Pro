import cv2
import pytesseract
import numpy as np
import re

# Glavna funkcija za ekstrakciju dimenzija iz slike zida
def extract_wall_data(image_path):
    """
    Analizira plan zida i vraća listu blokova sa dimenzijama.
    Vraća listu u formatu pogodnom za viewer2d/viewer3d.
    """
    try:
        # Učitavanje slike
        img = cv2.imread(image_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (3, 3), 0)

        # Detekcija ivica (linije zida)
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)

        # Detekcija linija Hough transformacijom
        lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=100, minLineLength=80, maxLineGap=10)

        # Prepoznavanje teksta (brojevi dimenzija)
        text = pytesseract.image_to_string(gray)
        numbers = re.findall(r"\d{2,4}", text)  # brojevi od 2 do 4 cifre

        # Osnovna pretpostavka: širine blokova su redom brojevi sa slike
        layout_data = []
        x_pos = 0
        height = 25  # visina bloka u cm (standard)
        block_types = ["Block", "Corner", "HalfBlock", "Ugaoni", "Modul"]

        for i, n in enumerate(numbers):
            width = int(n)
            block_type = block_types[i % len(block_types)]
            layout_data.append({
                "x": x_pos,
                "y": 0,
                "w": width,
                "h": height,
                "type": block_type
            })
            x_pos += width

        return layout_data

    except Exception as e:
        print("❌ Greška u analizi zida:", e)
        return []
