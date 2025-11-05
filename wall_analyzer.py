import cv2
import pytesseract
import numpy as np
import re

def extract_wall_data(image_path, return_debug=False):
    """
    Returns:
      - if return_debug=True: (layout_data, debug_images_dict)
      - else: layout_data
    layout_data is a list of dicts: {"x","y","w","h","type"}
    """
    dbg = {}

    img_color = cv2.imread(image_path)
    if img_color is None:
        return (None, dbg) if return_debug else None

    # 1) Grayscale
    gray = cv2.cvtColor(img_color, cv2.COLOR_BGR2GRAY)
    dbg["01_gray"] = gray

    # 2) Adaptive threshold (invert so black lines -> white)
    bw = cv2.adaptiveThreshold(
        gray, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV,
        31, 5
    )
    dbg["02_bw"] = bw

    # 3) Morphological close to connect thin segments
    kernel = np.ones((3, 3), np.uint8)
    bw_closed = cv2.morphologyEx(bw, cv2.MORPH_CLOSE, kernel, iterations=2)
    dbg["03_close"] = bw_closed

    # 4) Detect long horizontal lines (base line of wall)
    H, W = bw_closed.shape[:2]
    lines = cv2.HoughLinesP(
        bw_closed, 1, np.pi/180,
        threshold=150,
        minLineLength=max(120, W // 4),
        maxLineGap=12
    )

    line_vis = img_color.copy()
    horizontals = []
    if lines is not None:
        for x1, y1, x2, y2 in lines[:, 0]:
            if abs(y1 - y2) <= 4:  # horizontal
                horizontals.append((x1, y1, x2, y2))
                cv2.line(line_vis, (x1, y1), (x2, y2), (0, 255, 0), 2)
    dbg["04_lines"] = line_vis

    layout = []

    if horizontals:
        # Donja najduža vodoravna linija kao "baza" zida
        base = max(horizontals, key=lambda p: min(p[1], p[3]))
        x1, y1, x2, y2 = base
        wall_width = abs(x2 - x1)
        wall_height = max(25, int(wall_width * 0.08))  # plitka visina samo za prikaz

        # 3 segmenta radi vizuelizacije (uvek nešto prikažemo)
        layout = [
            {"x": int(x1),               "y": int(y1 - wall_height), "w": int(wall_width * 0.50), "h": int(wall_height), "type": "Block"},
            {"x": int(x1 + wall_width*0.50), "y": int(y1 - wall_height), "w": int(wall_width * 0.25), "h": int(wall_height), "type": "Corner"},
            {"x": int(x1 + wall_width*0.75), "y": int(y1 - wall_height), "w": int(wall_width * 0.25), "h": int(wall_height), "type": "HalfBlock"},
        ]

    if not layout:
        # Fallback: najveći spoljašnji kontur
        cnts, _ = cv2.findContours(bw_closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if cnts:
            c = max(cnts, key=cv2.contourArea)
            x, y, w, h = cv2.boundingRect(c)
            layout = [{"x": int(x), "y": int(y), "w": int(w), "h": max(25, int(h * 0.12)), "type": "Block"}]

    return (layout, dbg) if return_debug else layout


   
