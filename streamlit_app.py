import streamlit as st
from datetime import datetime
import os, tempfile
from PIL import Image
import numpy as np

# PDF konverzija
from pdf2image import convert_from_bytes

# Naši moduli
from wall_analyzer import extract_wall_data
from viewer2d import draw_wall_2d
from viewer3d import draw_wall_3d


# ------------------------------------------------------------
# FUNKCIJE
# ------------------------------------------------------------
def save_uploaded_image(uploaded_file):
    img = Image.open(uploaded_file).convert("RGB")
    fd, temp_path = tempfile.mkstemp(prefix="uploaded_", suffix=".png")
    os.close(fd)
    img.save(temp_path, "PNG")
    return temp_path


def save_pdf_first_page_as_png(uploaded_file):
    pages = convert_from_bytes(uploaded_file.read())
    fd, temp_path = tempfile.mkstemp(prefix="converted_", suffix=".png")
    os.close(fd)
    pages[0].save(temp_path, "PNG")
    return temp_path


# ------------------------------------------------------------
# APLIKACIJA
# ------------------------------------------------------------
st.set_page_config(page_title="MZ Wall Designer PRO v2.0", page_icon="🧱", layout="wide")

st.title("MZ WALL DESIGNER PRO v2.0")
st.subheader("Professional wall design and analysis software")
st.caption("(Modular thinking — smart construction)")

uploaded_file = st.file_uploader(
    "Upload wall plan image / Učitaj plan zida",
    type=["jpg", "jpeg", "png", "pdf"],
)

show_debug = st.sidebar.checkbox("Show debug images", value=True)

if uploaded_file:
    try:
        if uploaded_file.type == "application/pdf":
            temp_path = save_pdf_first_page_as_png(uploaded_file)
            st.info("📄 PDF prepoznat — konvertovan u sliku (PNG).")
        else:
            temp_path = save_uploaded_image(uploaded_file)

        st.image(temp_path, caption="Uploaded wall plan", use_column_width=True)
        st.success("✅ File uploaded successfully!")

        # Analiza zida
        result = extract_wall_data(temp_path, return_debug=show_debug)
        if isinstance(result, tuple):
            layout_data, dbg = result
        else:
            layout_data, dbg = result, {}

        if layout_data:
            st.success("✅ Wall structure detected.")
            draw_wall_2d(layout_data)
            draw_wall_3d(layout_data)
        else:
            st.error("⚠️ Could not detect wall structure. Please check image quality.")

        if show_debug and dbg:
            with st.expander("🧩 Debug: computer vision steps", expanded=True):
                for key, img in dbg.items():
                    st.image(img, caption=key, use_column_width=True)

    except Exception as e:
        st.error(f"❌ Greška: {e}")
