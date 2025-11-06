import streamlit as st
from datetime import datetime

st.set_page_config(
    page_title="MZ WALL DESIGNER PRO v2.0",
    page_icon="🧱",
    layout="wide",
    initial_sidebar_state="expanded"
)

if "lang" not in st.session_state:
    st.session_state.lang = "EN"

lang = st.sidebar.selectbox("Language / Jezik", ["EN", "SR"], index=0)
st.session_state.lang = lang

def t(en, sr):
    return en if st.session_state.lang == "EN" else sr

st.title("MZ WALL DESIGNER PRO v2.0")
st.subheader("Professional wall design and analysis software")
st.caption("(Modular thinking — smart construction)")

st.markdown("---")
st.write(t("Welcome! Upload your wall layout to begin.",
           "Dobrodošli! Učitajte raspored zida da započnete."))

uploaded_file = st.file_uploader(
    t("Upload wall plan image", "Učitaj sliku plana zida"),
    type=["jpg", "jpeg", "png", "pdf"]

)
if uploaded_file:
    import tempfile
    import os

    # Ako je PDF -> renderuj prvu stranicu u PNG preko PyMuPDF
    if uploaded_file.type == "application/pdf":
        try:
            import fitz  # PyMuPDF
        except ImportError:
            st.error("Missing dependency 'pymupdf'. Add 'pymupdf' to requirements.txt and reboot the app.")
            st.stop()

        pdf_bytes = uploaded_file.read()
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        page = doc.load_page(0)              # prva stranica
        pix = page.get_pixmap(dpi=200)       # dovoljno kvalitetno za analizu
        temp_path = "converted_wall.png"
        pix.save(temp_path)
        display_image_path = temp_path

    else:
        # JPG/PNG putanja
        temp_path = "uploaded_wall.png"
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        display_image_path = temp_path

    st.image(display_image_path, caption=t("Uploaded wall plan", "Učitani plan zida"), use_column_width=True)
    st.success(t("File uploaded successfully!", "Datoteka uspešno učitana!"))



# simulacija rasporeda zida — placeholder podaci
from wall_analyzer import extract_wall_data

if uploaded_file:
    # Sačuvaj privremeno sliku
    temp_path = "uploaded_wall.jpg"
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

 # === Analysis section ===
# Prikaži internu analizu (debug)
show_debug = st.sidebar.checkbox("Show debug images", value=True)

if uploaded_file:
    # ovde već imaš kod za temp_path (ostavi ga)
    if show_debug:
        result = extract_wall_data(temp_path, return_debug=True)
        layout_data, dbg = result if isinstance(result, tuple) else (result, {})
    else:
        layout_data = extract_wall_data(temp_path)
        dbg = {}

    if layout_data:
    st.success("✅ Wall structure detected.")

    # 2D prikaz
    from viewer2d import draw_wall_2d
    draw_wall_2d(layout_data)

    # 3D prikaz
    from viewer3d import draw_wall_3d
    draw_wall_3d(layout_data)
else:
    st.error("⚠️ Could not detect wall structure. Please check image quality.")

# Debug slike uvek prikaži, čak i ako nije pronađen zid
if show_debug and dbg:
    with st.expander("🧩 Debug: computer vision steps", expanded=True):
        for key in sorted(dbg.keys()):
            st.image(dbg[key], caption=key, use_column_width=True)

  





