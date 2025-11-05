import streamlit as st
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import random

def draw_wall_3d(layout_data, title="3D Wall View"):
    """
    Prikazuje jednostavan 3D prikaz zida na osnovu layout_data.
    layout_data: lista dict-ova sa ključevima: x, y, w, h, type
    """
    fig = plt.figure(figsize=(10, 6))
    ax = fig.add_subplot(111, projection='3d')
    ax.set_title(title, fontsize=14, fontweight="bold")

    # Postavke osa
    ax.set_xlabel("Width (cm)")
    ax.set_ylabel("Height (cm)")
    ax.set_zlabel("Depth (cm)")

    # Generiši pseudo-dubinu (debljinu zida)
    wall_depth = 25

    colors = ["#88d3c7", "#fff5b3", "#bbebda", "#fb8072", "#80b1d3", "#fdb462"]

    for b in layout_data:
        x = float(b.get("x", 0))
        y = float(b.get("y", 0))
        w = float(b.get("w", 10))
        h = float(b.get("h", 10))
        t = b.get("type", "")
        color = random.choice(colors)

        # Površina zida (blok)
        X = [x, x+w, x+w, x, x]
        Y = [y, y, y+h, y+h, y]
        Z = [0, 0, 0, 0, 0]

        ax.plot_trisurf(X, Y, Z, color=color, alpha=0.8)
        ax.plot_trisurf(X, Y, [wall_depth]*5, color=color, alpha=0.5)

    ax.view_init(elev=25, azim=-60)
    st.subheader("🧱 3D Wall Layout Preview")
    st.pyplot(fig)
