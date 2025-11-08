# MZ_WALLDESIGNER_PRO / wall_analyzer.py
# ------------------------------------------------------------
# Autor: Moca Zižić & GPT-5 Thinking
# Datum: 2025-11-08
#
# Ovaj modul obezbeđuje dva ulazna režima:
#  1) "manual"  – ručni unos dimenzija zida i svih otvora
#  2) "auto"    – analiza slike/PDF-a (OpenCV konture; PDF preko pdf2image)
#
# API je kompatibilan sa postojećom aplikacijom:
#   extract_wall_data(input_mode="manual"|"auto",
#                     image=None, pdf_path=None,
#                     return_debug=False,
#                     dpi=200, use_poppler=True,
#                     manual_params=None)
#
# Vraća dict:
#  {
#    "wall": {"x":0,"y":0,"w":W,"h":H,"type":"wall"},
#    "openings": [ {x,y,w,h,type} ... ],
#    "blocks": [],                      # (popunjavamo u sledećoj iteraciji)
#    "dimensions": {"width_cm":W,"height_cm":H},
#    "scale": {"px_per_cm": px_per_cm}  # kod "manual" je 1:1 u cm koordinatama
#    "debug": {...}                     # samo ako return_debug=True
#  }
#
# Napomena:
#  - Koordinate su u centimetrima za "manual" (donji levi ugao zida je 0,0).
#  - Za "auto" detekciju radimo u pikselima; ako proslediš physical dimenzije
#    u manual_params={"width_cm":..., "height_cm":...}, mapiraćemo px->cm.
# ------------------------------------------------------------

from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple, Any

import numpy as np

# OpenCV je opciono; aplikacija sme da radi i bez njega u "manual" modu
try:
    import cv2
except Exception:
    cv2 = None

# pdf2image je opciono; koristi Poppler
try:
    from pdf2image import convert_from_path
except Exception:
    convert_from_path = None


# ---------------------------
# Pomoćne strukture i alati
# ---------------------------

@dataclass
class Rect:
    x: float
    y: float
    w: float
    h: float
    type: str = "rect"

    def as_dict(self) -> Dict[str, Any]:
        return {"x": float(self.x), "y": float(self.y), "w": float(self.w), "h": float(self.h), "type": self.type}


def _validate_manual(manual_params: Optional[Dict]) -> Tuple[float, float, List[Dict]]:
    """
    Validacija ručnog unosa.
    manual_params očekuje:
      {
        "width_cm": float,
        "height_cm": float,
        "openings": [ {"x":..,"y":..,"w":..,"h":..,"type":"window"|"door"|"opening"}, ... ]
      }
    """
    if not manual_params:
        raise ValueError("manual_params je obavezan kada je input_mode='manual'.")

    try:
        W = float(manual_params["width_cm"])
        H = float(manual_params["height_cm"])
    except Exception:
        raise ValueError("Nedostaju 'width_cm' i/ili 'height_cm' u manual_params.")

    if W <= 0 or H <= 0:
        raise ValueError("Dimenzije zida moraju biti pozitivne (width_cm, height_cm).")

    openings = manual_params.get("openings", []) or []

    # Proveri da li su svi otvori unutar zida
    sanitized = []
    for i, o in enumerate(openings):
        x = float(o["x"]); y = float(o["y"]); w = float(o["w"]); h = float(o["h"])
        t = str(o.get("type", "opening"))
        if w <= 0 or h <= 0:
            raise ValueError(f"Otvor {i+1}: širina/visina moraju biti > 0.")
        if x < 0 or y < 0 or x + w > W + 1e-6 or y + h > H + 1e-6:
            raise ValueError(f"Otvor {i+1} izlazi izvan granica zida (0..{W}, 0..{H}).")
        sanitized.append({"x": x, "y": y, "w": w, "h": h, "type": t})

    return W, H, sanitized


def _pack_debug(**kwargs) -> Dict[str, Any]:
    out = {}
    for k, v in kwargs.items():
        out[k] = v
    return out


# ----------------------------------------------------
# PDF -> slika (prva stranica), uz opcioni Poppler
# ----------------------------------------------------
def _load_image_from_pdf(pdf_path: str, dpi: int = 200, use_poppler: bool = True) -> Optional[np.ndarray]:
    if convert_from_path is None:
        return None
    try:
        images = convert_from_path(pdf_path, dpi=dpi, use_pdftocairo=use_poppler)
        if not images:
            return None
        # Uzmemo prvu stranicu
        img = np.array(images[0])[:, :, ::-1]  # PIL->OpenCV (BGR)
        return img
    except Exception:
        return None


# ----------------------------------------------------
# Detekcija kontura (AUTO mód, OpenCV)
# ----------------------------------------------------
def _auto_detect_geometry(image_bgr: np.ndarray,
                          known_wall_cm: Optional[Tuple[float, float]] = None,
                          return_debug: bool = False) -> Tuple[Dict, Optional[Dict]]:
    """
    Vraća minimalan set: wall rect (u px ili cm), openings[] (u istoj jedinici),
    i px_per_cm ako je poznato (ako su prosleđene fizičke dimenzije zida).
    """
    if cv2 is None:
        raise RuntimeError("OpenCV (cv2) nije dostupan. Instaliraj opencv-python ili koristi 'manual' režim.")

    dbg = {}

    # 1) sivo + filtriranje
    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)

    # 2) adaptivni threshold + morf. zatvaranje
    th = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                               cv2.THRESH_BINARY_INV, 35, 8)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    closed = cv2.morphologyEx(th, cv2.MORPH_CLOSE, kernel, iterations=2)

    # 3) Canny (pomogne stabilnosti rubova)
    edges = cv2.Canny(blur, 50, 150)
    union = cv2.bitwise_or(closed, edges)

    # 4) konture
    cnts, _ = cv2.findContours(union, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not cnts:
        raise RuntimeError("Nisam našao konture na slici – proveri kontrast/plansku liniju.")

    # pretpostavimo: najveća pravougaona kontura je spoljašnji zid
    H, W = gray.shape[:2]
    area_img = W * H

    wall_rect_px = None
    candidates = []
    for c in cnts:
        area = cv2.contourArea(c)
        if area < 0.005 * area_img:
            continue  # ignoriši premale
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02 * peri, True)
        x, y, w, h = cv2.boundingRect(approx)
        aspect = w / max(1, h)
        candidates.append((area, (x, y, w, h), approx, aspect))

    if not candidates:
        raise RuntimeError("Nema validnih većih kontura – ne mogu da izvučem zid.")

    # najveća
    candidates.sort(key=lambda z: z[0], reverse=True)
    wall_xywh = candidates[0][1]
    wall_rect_px = Rect(*wall_xywh, type="wall")

    # openings: probajmo da nađemo "rupe" preko hijerarhije kontura
    # Za jednostavnost: izdvoji sve pravougaonike unutar zida koji nisu preveliki.
    cnts_all, hier = cv2.findContours(union, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    openings_px = []
    if hier is not None:
        wall_x, wall_y, wall_w, wall_h = wall_xywh
        for i, c in enumerate(cnts_all):
            x, y, w, h = cv2.boundingRect(c)
            if x <= wall_x + 2 or y <= wall_y + 2 or x + w >= wall_x + wall_w - 2 or y + h >= wall_y + wall_h - 2:
                # dodiruje granicu zida -> nije otvor
                continue
            area = w * h
            if area < 0.001 * area_img:
                continue
            # heuristika: otvori imaju približno prave uglove
            peri = cv2.arcLength(c, True)
            approx = cv2.approxPolyDP(c, 0.02 * peri, True)
            if len(approx) >= 4 and len(approx) <= 6:
                openings_px.append(Rect(x, y, w, h, type="opening").as_dict())

    # mapiranje px->cm ako znamo fizičke dimenzije spoljnog zida
    scale = {"px_per_cm": None}
    if known_wall_cm is not None:
        target_w_cm, target_h_cm = known_wall_cm
        px_per_cm_x = wall_rect_px.w / max(1e-6, target_w_cm)
        px_per_cm_y = wall_rect_px.h / max(1e-6, target_h_cm)
        px_per_cm = (px_per_cm_x + px_per_cm_y) / 2.0
        scale["px_per_cm"] = float(px_per_cm)

        # konvertuj sve u cm sa donjim levim poreklom
        def px_to_cm_rect(r: Dict[str, float]) -> Dict[str, float]:
            # OpenCV ima poreklo u gornjem levom, y na dole;
            # prebacujemo u koordinatni sistem sa (0,0) u DONJEM levom
            x_cm = (r["x"] - wall_rect_px.x) / px_per_cm
            # inverzija y:
            y_top_px = r["y"] - wall_rect_px.y
            y_bottom_cm = (wall_rect_px.h - (y_top_px + r["h"])) / px_per_cm
            return {"x": x_cm, "y": y_bottom_cm, "w": r["w"] / px_per_cm, "h": r["h"] / px_per_cm, "type": r["type"]}

        wall_cm = Rect(0.0, 0.0, target_w_cm, target_h_cm, type="wall").as_dict()
        openings_cm = [px_to_cm_rect(o) for o in openings_px]
        result = {
            "wall": wall_cm,
            "openings": openings_cm,
            "blocks": [],
            "dimensions": {"width_cm": float(target_w_cm), "height_cm": float(target_h_cm)},
            "scale": scale,
        }
    else:
        # ostavi u pikselima; vieweri i dalje mogu da prikažu (tretiraj kao "cm")
        # ali preporuka je da "manual_params" sadrži width/height radi skaliranja.
        # takođe, poreklo korigujemo na donji levi u okviru wall bbox-a
        wall_cm_like = Rect(0.0, 0.0, wall_rect_px.w, wall_rect_px.h, type="wall").as_dict()

        # premapiraj otvore u odnosu na dno
        conv = []
        for o in openings_px:
            y_bottom = (wall_rect_px.h - ((o["y"] - wall_rect_px.y) + o["h"]))
            conv.append({"x": o["x"] - wall_rect_px.x, "y": y_bottom, "w": o["w"], "h": o["h"], "type": o["type"]})

        result = {
            "wall": wall_cm_like,
            "openings": conv,
            "blocks": [],
            "dimensions": {"width_cm": float(wall_rect_px.w), "height_cm": float(wall_rect_px.h)},
            "scale": scale,
        }

    if return_debug:
        dbg = _pack_debug(
            gray=gray,
            thresh=th,
            closed=closed,
            edges=edges,
            union=union,
            wall_bbox_px=wall_rect_px.as_dict(),
            openings_px=openings_px,
        )
        result["debug"] = dbg

    return result, (dbg if return_debug else None)


# ----------------------------------------------------
# JAVNI API
# ----------------------------------------------------
def extract_wall_data(input_mode: str = "manual",
                      image: Optional[np.ndarray] = None,
                      pdf_path: Optional[str] = None,
                      return_debug: bool = False,
                      dpi: int = 200,
                      use_poppler: bool = True,
                      manual_params: Optional[Dict] = None) -> Dict[str, Any]:
    """
    Glavni ulaz za aplikaciju (kompatibilan sa starim pozivanjem).

    input_mode:
      - "manual": koristi manual_params (cm koordinate, (0,0) donji levi ugao)
      - "auto":   koristi image ili pdf_path i pokušava konture

    manual_params:
      {
        "width_cm": float,
        "height_cm": float,
        "openings": [ {"x":..,"y":..,"w":..,"h":..,"type": "opening"|"window"|"door"}, ... ]
      }

    Vraća dict kao u zaglavlju fajla.
    """
    if input_mode not in ("manual", "auto"):
        raise ValueError("input_mode mora biti 'manual' ili 'auto'.")

    # ----- MANUAL -----
    if input_mode == "manual":
        W, H, openings = _validate_manual(manual_params)
        result = {
            "wall": Rect(0.0, 0.0, W, H, type="wall").as_dict(),
            "openings": openings,
            "blocks": [],  # raspored blokova ubacujemo u sledećoj iteraciji
            "dimensions": {"width_cm": float(W), "height_cm": float(H)},
            "scale": {"px_per_cm": 1.0},  # radimo direktno u cm jedinicama
        }
        if return_debug:
            result["debug"] = _pack_debug(source="manual", note="Ručni unos validiran.")
        return result

    # ----- AUTO (slika ili PDF) -----
    # U ovom modu pokušavamo automatsku detekciju kontura.
    # Ako manual_params sadrži width_cm/height_cm, koristi se za skaliranje.
    if input_mode == "auto":
        img = None
        if image is not None:
            img = image.copy()
        elif pdf_path:
            img = _load_image_from_pdf(pdf_path, dpi=dpi, use_poppler=use_poppler)
            if img is None:
                raise RuntimeError(
                    "Ne mogu da pretvorim PDF u sliku. Proveri da li je Poppler instaliran "
                    "ili prosledi 'use_poppler=False' ako imaš pdftocairo u PATH-u."
                )
        else:
            raise ValueError("Za 'auto' režim prosledi 'image' ili 'pdf_path'.")

        known = None
        if manual_params and "width_cm" in manual_params and "height_cm" in manual_params:
            known = (float(manual_params["width_cm"]), float(manual_params["height_cm"]))

        result, _ = _auto_detect_geometry(img, known_wall_cm=known, return_debug=return_debug)
        return result
