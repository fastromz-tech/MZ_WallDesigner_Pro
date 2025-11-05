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
    t("Upload wall plan image", "Učitaj sliku plana zida"), type=["jpg", "png"]
)
if uploaded_file:
    st.image(uploaded_file, caption=t("Uploaded wall plan", "Učitani plan zida"), use_column_width=True)
    st.success(t("File uploaded successfully!", "Datoteka uspešno učitana!"))
    from viewer2d import draw_wall_2d

# simulacija rasporeda zida — placeholder podaci
from wall_analyzer import extract_wall_data

if uploaded_file:
    # Sačuvaj privremeno sliku
    temp_path = "uploaded_wall.jpg"
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    # Analiza zida pomoću AI-a
    st.info("🔍 Analyzing wall layout, please wait...")
    layout_data = extract_wall_data(temp_path)

    if layout_data:
        st.success("✅ Wall dimensions successfully detected!")
        from viewer2d import draw_wall_2d
        draw_wall_2d(layout_data)

        from viewer3d import draw_wall_3d
        draw_wall_3d(layout_data)
    else:
        st.error("⚠️ Could not detect wall structure. Please check image quality.")


from viewer3d import draw_wall_3d
draw_wall_3d(layout_data)




