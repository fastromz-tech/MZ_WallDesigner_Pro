import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches


def draw_wall_2d(layout_data):
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.set_title("🧱 2D Wall Layout Preview")
    ax.set_xlabel("X axis")
    ax.set_ylabel("Y axis")
    ax.grid(True)

    # Tekstualne informacije iz layout_data
    text = f"Contours: {layout_data.get('contour_count', 0)}\nNumbers: {layout_data.get('numbers', [])}"
    ax.text(0.5, 0.5, text, ha="center", va="center", fontsize=10)

    st.pyplot(fig)
