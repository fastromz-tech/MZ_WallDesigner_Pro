import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Paleta za tipove (maks 9 različitih)
TYPE_COLORS = [
    "#88d3c7", "#fff5b3", "#bbebda", "#fb8072", "#80b1d3",
    "#fdb462", "#b3de69", "#fccde5", "#d9d9d9"
]

# Mapiranje string oznaka na indekse boja
TYPE_LOOKUP = {
    "block": 0, "1": 0,
    "corner": 1, "3": 1,
    "halfblock": 2, "2": 2,
    "edge": 3, "4": 3,
    "half-edge": 4, "5": 4,
    "y": 5, "a": 6, "b": 7,  # grede
}

def _color_index(t):
    """Vrati indeks boje (0..len-1) za dati tip bloka (broj ili string)."""
    if t is None:
        return 0
    # probaj kao broj: 1,2,3...
    try:
        return max(0, int(t) - 1) % len(TYPE_COLORS)
    except Exception:
        # probaj kao string
        key = str(t).strip().lower()
        return TYPE_LOOKUP.get(key, 0)

def draw_wall_2d(layout_data, title="2D Wall View"):
    """
    layout_data: lista dict-ova sa ključevima: x, y, w, h, type
    (x,y) gore-levo, dimenzije u cm.
    """
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.set_title(title, fontsize=14, fontweight="bold")
    ax.set_xlabel("Width (cm)")
    ax.set_ylabel("Height (cm)")
    ax.set_aspect("equal")

    # automatske granice po sadržaju
    max_x = 0
    max_y = 0

    for b in layout_data:
        x = float(b.get("x", 0))
        y = float(b.get("y", 0))
        w = float(b.get("w", 10))
        h = float(b.get("h", 10))
        idx = _color_index(b.get("type"))

        rect = patches.Rectangle(
            (x, y), w, h,
            linewidth=1,
            edgecolor="black",
            facecolor=TYPE_COLORS[idx],
            alpha=0.85,
        )
        ax.add_patch(rect)

        label = str(b.get("type", ""))
        if label:
            ax.text(x + w/2, y + h/2, label, ha="center", va="center", fontsize=8)

        max_x = max(max_x, x + w)
        max_y = max(max_y, y + h)

    ax.set_xlim(0, max(10, max_x * 1.05))
    ax.set_ylim(0, max(10, max_y * 1.05))
    ax.invert_yaxis()  # da (0,0) bude gore-levo kao na crtežu
    plt.tight_layout()

    # direktno prikaži u Streamlit-u
    st.subheader("🧩 2D Wall Layout Preview")
    st.pyplot(fig)
