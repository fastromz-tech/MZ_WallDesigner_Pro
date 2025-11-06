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

    # Učitavanje slike
    img = cv2.imread(image_path)
    if img is None:
        return (None, dbg) if return_debug else None

    # Siva skala
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    dbg["01_gray"] = gray

    # Blagi blur da uklonimo šum
    blur = cv2.GaussianBlur(gray, (3, 3), 0)
    dbg["02_blur"] = blur

    # Adaptivni threshold + invert (za crne CAD linije na beloj pozadini)
    bw = cv2.adaptiveThreshold(
        blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 25, 10
    )
    dbg["03_binary_inv"] = bw

    # Zatvaranje rupa i prekida
    kernel = np.ones((3, 3), np.uint8)
    closed = cv2.morphologyEx(bw, cv2.MORPH_CLOSE, kernel, iterations=2)
    dbg["04_closed"] = closed

    # Detekcija kontura
    contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    vis = img.copy()

    if contours:
        # Nacrtaj sve konture za pregled
        for c in contours:
            area = cv2.contourArea(c)
            if area > 500:  # ignorišemo male brojeve i oznake
                cv2.drawContours(vis, [c], -1, (0, 255, 0), 2)
        dbg["05_all_contours"] = vis

        # Najveća kontura = zid
        c = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(c)
        cv2.rectangle(vis, (x, y), (x + w, y + h), (0, 0, 255), 2)
        dbg["06_detected_wall"] = vis

        layout = [{"x": int(x), "y": int(y), "w": int(w), "h": int(h), "type": "Wall"}]
        return (layout, dbg) if return_debug else layout

    else:
        # Ako nema kontura, ipak pošalji slike
        dbg["05_all_contours"] = img
        return (None, dbg) if return_debug else None

   
