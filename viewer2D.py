import matplotlib.pyplot as plt
import matplotlib.patches as patches

def draw_wall_2d(layout_data, title="2D Wall View"):
    """
    Draws a simplified 2D wall view with different colors for block types.
    layout_data = list of dicts with keys: x, y, w, h, type
    """
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.set_title(title, fontsize=14, fontweight="bold")
    ax.set_xlim(0, 700)
    ax.set_ylim(0, 300)
    ax.set_xlabel("Width (cm)")
    ax.set_ylabel("Height (cm)")
    ax.set_aspect("equal")

    colors = ["#8dd3c7", "#ffffb3", "#bebada", "#fb8072", "#80b1d3", "#fdb462", "#b3de69", "#fccde5"]

    for b in layout_data:
        rect = patches.Rectangle(
            (b["x"], b["y"]),
            b["w"],
            b["h"],
            linewidth=1,
            edgecolor="black",
            facecolor=colors[(b["type"] - 1) % len(colors)],
        )
        ax.add_patch(rect)
        ax.text(
            b["x"] + b["w"] / 2,
            b["y"] + b["h"] / 2,
            str(b["type"]),
            ha="center",
            va="center",
            fontsize=10,
            fontweight="bold",
        )

    plt.gca().invert_yaxis()
    plt.tight_layout()
    return fig
