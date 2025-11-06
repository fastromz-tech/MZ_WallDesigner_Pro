import streamlit as st
import plotly.graph_objects as go


def draw_wall_3d(layout_data):
    fig = go.Figure(
        data=[
            go.Mesh3d(
                x=[0, 1, 1, 0],
                y=[0, 0, 1, 1],
                z=[0, 0, 0, 0.5],
                color='lightblue',
                opacity=0.70,
            )
        ]
    )
    fig.update_layout(
        scene=dict(
            xaxis_title='X',
            yaxis_title='Y',
            zaxis_title='Z',
        ),
        title="3D Wall Layout Preview",
    )
    st.plotly_chart(fig, use_container_width=True)

