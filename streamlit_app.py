# --- UI / osnovno ---
import streamlit as st
from datetime import datetime

# --- CV/obrada (ovo već imaš na vrhu, ostavljam zbog potpunosti) ---
import cv2
import pytesseract
import numpy as np
import re

# --- ostalo za fajlove/slike ---
from io import BytesIO
from PIL import Image
import os
import tempfile

# Pokušaj da uvezeš PDF->slika konverziju (nije obavezno, ali omogućava rad sa PDF-om)
try:
    from pdf2image import convert_from_bytes
    PDF2IMAGE_OK = True
except Exception:
    PDF2IMAGE_OK = False

# Naše lokalne funkcije
from wall_analyzer import extract_wall_data  # analiza slike → layout_data (+ debug)
# draw funkcije se uvoze *u trenutku* kada su potrebne (da bi greške bile jasnije)
# from viewer2d import draw_wall_2d
# from viewer3d import draw_wall_3d


# ------------------------------------------------------------
# POMOĆNE FUNKCIJE
# ------------------------------------------------------------
def save_uploaded_image(uploaded_file) -> str:
    """
    Prima: Streamlit UploadedFile (PNG/JPG/JPEG)
    Vraća: putanja do privremene PNG slike na disku.
    """
    img = Image.open(uploaded_file).convert("RGB")
    fd, temp_path = tempfile.mkstemp(prefix="uploaded_", suffix=".png")
    os.close(fd)
    img.save(temp_path, format="PNG")
    return temp_path


def save_pdf_first_page_as_png(uploaded_file) -> str:
    """
    Prima: PDF (UploadedFile)
    Vraća: putanja do PNG fajla (samo prva stranica).
    Baća izuzetak ako pdf2image nije dostupna.
    """
    if not PDF2IMAGE_OK:
        raise RuntimeError(
            "PDF podrška nije dostupna (pdf2image nije instaliran). "
            "Molim konvertuj PDF u PNG/JPG i ponovo otpremi."
        )
    pages = convert_from_bytes(uploaded_file.read())
    if not pages:
        raise RuntimeError("PDF je prazan ili nečitljiv.")
    fd, temp_path = tempfile.mkstemp(prefix="converted_", suffix=".png")
    os.close(fd)
    pages[0].save(temp_path, "PNG")
    return temp_path


# ------------------------------------------------------------
# APLIKACIJA
# ------------------------------------------------------------
st.set_page_config(
    page_title="MZ WALL DESIGNER PRO v2.0",
    page_icon="🧱",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Jezik (trenutno je UI engleski/srpski samo u natpisima; analiza je ista)
if "lang" not in st.session_state:
    st.session_state.lang = "EN"
lang = st.sidebar.selectbox("Language / Jezik", ["EN", "SR"], index=0)
st.session_state.lang = lang

title_text = "MZ WALL DESIGNER PRO v2.0" if lang == "EN" else "MZ WALL DESIGNER PRO v2.0"
subtitle_text = (
    "Professional wall design and analysis software"
    if lang == "EN"
    else "Profesionalni softver za dizajn i analizu zidova"
)

st.title(title_text)
st.subheader(subtitle_text)
st.caption("(Modular thinking — smart construction)")

# Podešavanje i uvoz fajla
uploaded_file = st.file_uploader(
    "Upload wall plan image / Učitaj sliku plana zida",
    type=["jpg", "jpeg", "png", "pdf"],
)

# Debug prekidač (prikaz internih koraka obrade slike)
show_debug = st.sidebar.checkbox("Show debug images", value=True)

if uploaded_file:
    # 1) Snimi u privremenu PNG sliku (ili PDF → PNG)
    try:
        if uploaded_file.type == "application/pdf":
            temp_path = save_pdf_first_page_as_png(uploaded_file)
            st.info("📄 PDF detektovan → prva stranica konvertovana u PNG.")
        else:
            temp_path = save_uploaded_image(uploaded_file)

        # Prikaži učitanu sliku
        st.image(temp_path, caption="Uploaded wall plan", use_column_width=True)
        st.success("File uploaded successfully!")

    except Exception as e:
        st.error(f"Greška pri pripremi fajla: {e}")
        temp_path = None

    # 2) Ako imamo pripremljenu PNG sliku, pokreni analizu
    if temp_path:
        try:
            # Ako želiš debug slike, tražimo ih iz analizera
            if show_debug:
                result = extract_wall_data(temp_path, return_debug=True)
                if isinstance(result, tuple):
                    layout_data, dbg = result
                else:
                    # fallback ako funkcija vrati samo layout_data
                    layout_data, dbg = result, {}
            else:
                layout_data = extract_wall_data(temp_path)
                dbg = {}

        except Exception as e:
            st.error(f"Greška pri analizi zida: {e}")
            layout_data, dbg = None, {}

        # 3) Prikaz rezultata
        if layout_data:
            st.success("✅ Wall structure detected.")

            # 2D i 3D prikaz — uvozimo ovde da bi poruke o greškama bile jasnije
            try:
                from viewer2d import draw_wall_2d
                draw_wall_2d(layout_data)
            except Exception as e:
                st.warning(f"(2D) Problem pri crtanju: {e}")

            try:
                from viewer3d import draw_wall_3d
                draw_wall_3d(layout_data)
            except Exception as e:
                st.warning(f"(3D) Problem pri crtanju: {e}")

        else:
            st.error("⚠️ Could not detect wall structure. Please check image quality.")

        # 4) Debug prikaz (ako postoji)
        if show_debug and dbg:
            with st.expander("🧩 Debug: computer vision steps", expanded=True):
                # očekujemo da dbg bude dict naziv_koraka -> slika (np.ndarray ili PIL)
                for key in sorted(dbg.keys()):
                    try:
                        img = dbg[key]
                        # podrži i numpy i PIL
                        if isinstance(img, np.ndarray):
                            st.image(img, caption=key, use_column_width=True)
                        elif isinstance(img, Image.Image):
                            st.image(img, caption=key, use_column_width=True)
                        elif isinstance(img, (bytes, bytearray)):
                            st.image(Image.open(BytesIO(img)), caption=key, use_column_width=True)
                        else:
                            st.write(f"{key}: (nepoznat tip podataka za prikaz)")
                    except Exception as e:
                        st.write(f"{key}: (ne mogu da prikažem) — {e}")
