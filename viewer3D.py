import plotly.graph_objects as go

def draw_wall_3d(layout_data, title="3D Wall View"):
    """
    Renders a 3D wall layout using Plotly cubes.
    layout_data = list of dicts with x, y, z, w, h, d, type
    """
    fig = go.Figure()
    colors = ["#8dd3c7", "#ffffb3", "#bebada", "#fb8072",
              "#80b1d3", "#fdb462", "#b3de69", "#fccde5"]

    for b in layout_data:
        color = colors[(b["type"] - 1) % len(colors)]
        fig.add_trace(
            go.Mesh3d(
                x=[b["x"], b["x"] + b["w"], b["x"] + b["w"], b["x"],
                   b["x"], b["x"] + b["w"], b["x"] + b["w"], b["x"]],
                y=[b["y"], b["y"], b["y"] + b["h"], b["y"] + b["h"],
                   b["y"], b["y"], b["y"] + b["h"], b["y"] + b["h"]],
                z=[b["z"], b["z"], b["z"], b["z"],
                   b["z"] + b["d"], b["z"] + b["d"], b["z"] + b["d"], b["z"] + b["d"]],
                color=color,
                opacity=0.9,
                name=f"Block {b['type']}"
            )
        )

    fig.update_layout(
        title=title,
        scene=dict(
            xaxis_title="Width (cm)",
            yaxis_title="Height (cm)",
            zaxis_title="Depth (cm)",
            aspectratio=dict(x=2, y=1, z=0.3),
            camera=dict(eye=dict(x=1.5, y=-2, z=1))
        ),
        margin=dict(l=0, r=0, b=0, t=40),
    )

    return fig
