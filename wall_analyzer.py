import cv2
import pytesseract
import numpy as np
import re

def extract_wall_data(image_path, return_debug=False):
    """
    Analizira crtež zida i vraća listu segmenata zida.
    Ako return_debug=True, vraća i slike sa međurezultatima.
    """
    import cv2
    import numpy as np

    dbg = {}

    # Učitaj sliku u sivoj skali
    img = cv2.imread(image_path)
    if img is None:
        return (None, dbg) if return_debug else None

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    dbg["01_gray"] = gray

    # Ukloni šum i poboljšaj kontrast
    blur = cv2.GaussianBlur(gray, (3, 3), 0)
    dbg["02_blur"] = blur

    # Inverzija boja ako su linije tamne
    mean_val = np.mean(blur)
    if mean_val > 127:
        inv = cv2.bitwise_not(blur)
    else:
        inv = blur
    dbg["03_inverted"] = inv

    # Detekcija ivica (Canny sa manjim pragovima)
    edges = cv2.Canny(inv, 30, 100)
    dbg["04_edges"] = edges

    # Zatvaranje rupa u linijama
    kernel = np.ones((3, 3), np.uint8)
    closed = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel, iterations=2)
    dbg["05_closed"] = closed

    # Pronalaženje kontura
    contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Ako nema kontura, vrati None
    if not contours:
        return (None, dbg) if return_debug else None

    # Nacrtaj konture radi provere
    vis = img.copy()
    for c in contours:
        area = cv2.contourArea(c)
        if area > 500:  # ignoriši male konture (brojevi, tekst)
            x, y, w, h = cv2.boundingRect(c)
            cv2.rectangle(vis, (x, y), (x + w, y + h), (0, 255, 0), 2)
    dbg["06_detected_contours"] = vis

    # Odaberi najveću konturu – zid
    wall_contour = max(contours, key=cv2.contourArea)
    x, y, w, h = cv2.boundingRect(wall_contour)

    # Generiši osnovnu strukturu zida
    layout = [
        {"x": int(x), "y": int(y), "w": int(w), "h": int(h), "type": "Wall"}
    ]

    return (layout, dbg) if return_debug else layout

   


   
