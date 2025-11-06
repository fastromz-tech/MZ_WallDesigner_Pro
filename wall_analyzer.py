import cv2
import pytesseract
import numpy as np
import re

def extract_wall_data(image_path, return_debug=False):
    """
    Analizira crtež zida i vraća listu segmenata u formatu:
    [{"x": int, "y": int, "w": int, "h": int, "type": "Wall"}]
    Ako return_debug=True, vraća i dict sa debug slikama.
    """
    import cv2
    import numpy as np

    dbg = {}

    # 1) Učitavanje i sivo
    img = cv2.imread(image_path)
    if img is None:
        return (None, dbg) if return_debug else None
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    dbg["01_gray"] = gray

    # 2) Lagani blur (da ujednači tanke linije)
    blur = cv2.GaussianBlur(gray, (3, 3), 0)
    dbg["02_blur"] = blur

    # 3) Binarizacija (robustno, za tanke CAD linije)
    # adaptive + invert kako bismo imali bele linije na crnoj pozadini
    bin_img = cv2.adaptiveThreshold(
        blur, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 31, 15
    )
    dbg["03_bin_adapt_inv"] = bin_img

    # 4) "Čišćenje": zatvaranje sitnih prekida
    closed = cv2.morphologyEx(bin_img, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8), iterations=2)
    dbg["04_closed"] = closed

    H, W = closed.shape[:2]

    # 5) Isticanje horizontalnih linija (dugih)
    #    Koristimo horizontalni element veće širine (npr. W//15, max 120)
    k = max(20, min(120, W // 15))
    kernel_h = cv2.getStructuringElement(cv2.MORPH_RECT, (k, 1))
    horizontals = cv2.morphologyEx(closed, cv2.MORPH_OPEN, kernel_h, iterations=1)
    dbg["05_horizontals"] = horizontals

    # 6) Hough za horizontalne segmente
    edges = cv2.Canny(horizontals, 50, 150)
    dbg["06_canny_on_horiz"] = edges

    lines = cv2.HoughLinesP(
        edges, rho=1, theta=np.pi / 180, threshold=80, minLineLength=max(80, W // 6), maxLineGap=20
    )

    # 7) Ako nema linija, probaj fallback preko najveće konture (okvir zida)
    if lines is None or len(lines) == 0:
        contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            return (None, dbg) if return_debug else None
        # najveća kontura
        c = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(c)
        vis = img.copy()
        cv2.rectangle(vis, (x, y), (x + w, y + h), (0, 255, 0), 2)
        dbg["07_fallback_bbox"] = vis
        layout = [{"x": int(x), "y": int(y), "w": int(w), "h": int(h), "type": "Wall"}]
        return (layout, dbg) if return_debug else layout

    # 8) Izaberi NAJDUŽU horizontalnu liniju (tipično baznu/otprilike dnu)
    def length(l):
        x1, y1, x2, y2 = l[0]
        return np.hypot(x2 - x1, y2 - y1)

    lines_sorted = sorted(lines, key=length, reverse=True)
    x1, y1, x2, y2 = lines_sorted[0][0]

    # Ako linija nije sasvim horizontalna, prisili (uzmi y prosečno)
    y_base = int(round((y1 + y2) / 2))
    x_left = min(x1, x2)
    x_right = max(x1, x2)

    # 9) Proširi levo/desno do prvog većeg prekida (da uhvatimo ceo zid)
    #    Skrolujemo po bin_img po y_base i šetamo do rubova slike
    row = bin_img[y_base, :]

    # levo
    L = x_left
    while L > 1 and row[L - 1] > 0:
        L -= 1
    # desno
    R = x_right
    while R < W - 2 and row[R + 1] > 0:
        R += 1

    # 10) Odredi visinu zida: tražimo najveći "pravougaoni" region iznad linije
    #     jednostavno: idemo gore dok ima značajnih pikselâ u koloni [L:R]
    top = y_base
    col_strip = np.sum(bin_img[:, L:R] > 0, axis=1)  # broj „linijskih“ piksela po redu
    # tražimo prvi red od gore gde ima smislenog sadržaja (10% širine)
    threshold_strip = max(5, int(0.1 * (R - L)))
    for yy in range(y_base - 1, max(0, y_base - int(H * 0.9)), -1):
        if col_strip[yy] > threshold_strip:
            top = yy
        else:
            break

    x, y, w, h = L, min(top, y_base) - 1, (R - L), (y_base - min(top, y_base)) + 3
    # sanity
    x = max(0, x)
    y = max(0, y)
    w = max(10, w)
    h = max(10, h)

    vis = img.copy()
    # nacrtaj detektovanu baznu liniju i rezultat
    cv2.line(vis, (x1, y_base), (x2, y_base), (0, 255, 255), 2)
    cv2.rectangle(vis, (x, y), (x + w, y + h), (0, 255, 0), 2)
    dbg["07_detected_base_and_bbox"] = vis

    layout = [{"x": int(x), "y": int(y), "w": int(w), "h": int(h), "type": "Wall"}]
    return (layout, dbg) if return_debug else layout

   


   
