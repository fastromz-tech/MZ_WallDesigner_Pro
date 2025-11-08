# =========================================================
# MZ_WALLDESIGNER_PRO – WALL ANALYZER (potpuno funkcionalna verzija)
# Verzija: 2025.11.08
# =========================================================

import streamlit as st
import numpy as np
import cv2

def extract_wall_data(
    input_mode="manual",
    image=None,
    pdf_path=None,
    return_debug=False,
    manual_params=None,
    **kwargs
):
    """
    Glavna funkcija za unos i analizu zida.
    Sada podržava:
      - ručni unos (bez slike)
      - automatsku analizu slike
    """
    # --- NORMALIZACIJA MODA (dozvoljavamo različite stringove) ---
    input_mode = str(input_mode).strip().lower()
    if input_mode in ["manual", "man", "rucni", "ručni", "unos", "hand", "manual input"]:
        mode = "manual"
    elif input_mode in ["auto", "automatic", "pdf", "image", "detekcija", "upload"]:
        mode = "auto"
    else:
        # Ako ništa od ovoga – defaultno ručni unos
        st.warning("Nepoznat input_mode – prelazim na ručni unos.")
        mode = "manual"

    # =========================================================
    # RUČNI UNOS – koristi se kada nema slike
    # =========================================================
    if mode == "manual":
        st.subheader("🧱 Ručni unos dimenzija zida i otvora")

        if not manual_params:
            manual_params = {}

        wall_width = st.number_input(
            "Širina zida (cm)", min_value=100.0, value=678.0, step=1.0
        )
        wall_height = st.number_input(
            "Visina zida (cm)", min_value=100.0, value=300.0, step=1.0
        )

        num_openings = st.number_input(
            "Broj otvora (prozori / vrata)", min_value=0, max_value=10, value=3, step=1
        )

        openings = []
        for i in range(int(num_openings)):
            st.markdown(f"### Otvor {i+1}")
            otype = st.selectbox(
                f"Tip otvora {i+1}", ["window", "door", "opening"], key=f"otype_{i}"
            )
            ox = st.number_input(f"X pozicija (cm) otvor {i+1}", 0.0, wall_width, 0.0, key=f"ox_{i}")
            oy = st.number_input(f"Y pozicija (cm) otvor {i+1}", 0.0, wall_height, 0.0, key=f"oy_{i}")
            ow = st.number_input(f"Širina otvora {i+1} (cm)", 10.0, wall_width, 100.0, key=f"ow_{i}")
            oh = st.number_input(f"Visina otvora {i+1} (cm)", 10.0, wall_height, 100.0, key=f"oh_{i}")

            openings.append({"x": ox, "y": oy, "w": ow, "h": oh, "type": otype})

        wall = {"x": 0.0, "y": 0.0, "w": wall_width, "h": wall_height, "type": "wall"}

        # Opcioni unos blokova
        st.subheader("🧩 Ručni unos blokova (opciono)")
        num_blocks = st.number_input("Broj blokova (opciono)", min_value=0, max_value=100, value=0)
        blocks = []
        for j in range(int(num_blocks)):
            bx = st.number_input(f"Block {j+1} X (cm)", 0.0, wall_width, 0.0, key=f"bx_{j}")
            by = st.number_input(f"Block {j+1} Y (cm)", 0.0, wall_height, 0.0, key=f"by_{j}")
            bw = st.number_input(f"Block {j+1} širina (cm)", 10.0, wall_width, 50.0, key=f"bw_{j}")
            bh = st.number_input(f"Block {j+1} visina (cm)", 10.0, wall_height, 25.0, key=f"bh_{j}")
            blocks.append({"x": bx, "y": by, "w": bw, "h": bh, "type": "block"})

        data = {
            "wall": wall,
            "openings": openings,
            "blocks": blocks,
            "dimensions": {"width_cm": wall_width, "height_cm": wall_height},
            "scale": {"px_per_cm": 1.0},
        }

        if return_debug:
            data["debug"] = {"note": "Manual mode active", "input_count": len(openings)}

        return data

    # =========================================================

