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
    from viewer2D import display_2d_layout
    display_2d_layout(uploaded_file)

