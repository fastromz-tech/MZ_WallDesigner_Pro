import cv2
import pytesseract
import numpy as np
import re


def extract_wall_data(image_path, return_debug=False):
    debug = {}

    # Učitaj sliku
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError("Slika nije učitana. Proveri format fajla.")
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (3, 3), 0)
    edges = cv2.Canny(blur, 50, 150)
    debug["Edges"] = edges

    # Detekcija kontura
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contoured = img.copy()
    cv2.drawContours(contoured, contours, -1, (0, 255, 0), 2)
    debug["Contours"] = contoured

    # OCR – prepoznavanje brojeva
    text = pytesseract.image_to_string(gray)
    numbers = re.findall(r"\d{2,4}", text)

    # Rezultati
    layout_data = {
        "contour_count": len(contours),
        "numbers": numbers,
    }

    if return_debug:
        return layout_data, debug
    return layout_data
