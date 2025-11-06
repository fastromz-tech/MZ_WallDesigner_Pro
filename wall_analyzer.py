import cv2
import pytesseract
import numpy as np
import re

def extract_wall_data(image_path, return_debug=False):
    """
    Analizira crtež zida i vraća listu segmenata.
    Ako return_debug=True, vraća i slike za debug prikaz.
    """
    import cv2
    import numpy as np

    dbg = {}

    # Učitaj sliku
    img = cv2.imread(image_path)
    if img is None:
        dbg["error"] = "Ne mogu da učitam sliku."
        return (None, dbg) if return_debug else None

    # Pretvori u sivu
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    dbg["01_gray"] = gray

    # Blagi blur (da smanji šum)
    blur = cv2.GaussianBlur(gray, (3, 3), 0)
    dbg["02_blur"] = blur

    # Adaptivni threshold (detekcija tankih linija)
    bw = cv2.adaptiveThreshold(
        blur, 255,
        cv2.ADAPTIVE_THRESH_MEAN_C,
        cv2.THRESH_BINARY_INV,
        25, 15
    )
    dbg["03_threshold"] = bw

    # Morfološko zatvaranje (da spoji prekinute linije)
    kernel = np.ones((3, 3), np.uint8)
    closed = cv2.morphologyEx(bw, cv2.MORPH_CLOSE, kernel, iterations=2)
    dbg["04_closed"] = closed

    # Detekcija kontura
    contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    vis = img.copy()

    # Ako nema kontura, makar prikaži šta imamo
    if not contours:
        dbg["05_no_contours"] = closed
        return (None, dbg) if return_debug else None

    # Nacrtaj sve konture
    for c in contours:
        cv2.drawContours(vis, [c], -1, (0, 255, 0), 1)
    dbg["05_all_contours"] = vis.copy()

    # Filtriraj konture po površini
    valid_contours = [c for c in contours if cv2.contourArea(c) > 100]
    dbg["06_filtered_contours"] = vis.copy()
    for c in valid_contours:
        x, y, w, h = cv2.boundingRect(c)
        cv2.rectangle(dbg["06_filtered_contours"], (x, y), (x + w, y + h), (255, 0, 0), 2)

    # Ako nema validnih kontura, prikaži sve i vrati None
    if not valid_contours:
        dbg["07_result"] = dbg["06_filtered_contours"]
        return (None, dbg) if return_debug else None

    # Najveća kontura = zid
    c = max(valid_contours, key=cv2.contourArea)
    x, y, w, h = cv2.boundingRect(c)
    cv2.rectangle(vis, (x, y), (x + w, y + h), (0, 0, 255), 3)
    dbg["07_result"] = vis

    layout = [{"x": int(x), "y": int(y), "w": int(w), "h": int(h), "type": "Wall"}]
    return (layout, dbg) if return_debug else layout

    
