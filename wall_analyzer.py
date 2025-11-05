import cv2
import pytesseract
import numpy as np
import re

def extract_wall_data(image_path):
    import cv2
    import numpy as np

    # Učitaj sliku u sivoj skali
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        return None

    # Poboljšaj kontrast
    img = cv2.equalizeHist(img)

    # Blagi blur da ukloni šum
    blurred = cv2.GaussianBlur(img, (5, 5), 0)

    # Automatsko podešavanje praga za ivice
    edges = cv2.Canny(blurred, 30, 120)

    # Pronalaženje kontura
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    wall_data = []
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        # Uzimamo samo veće oblike (da ignorišemo oznake, tekst, male brojeve)
        if w > 50 and h > 15:
            wall_data.append({"x": int(x), "y": int(y), "w": int(w), "h": int(h), "type": "Block"})

    if not wall_data:
        return None

    return wall_data
