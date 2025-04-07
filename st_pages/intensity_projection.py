import streamlit as st
import math
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import plotly.graph_objects as go

with st.expander("**Description**", expanded=True):
    st.markdown("""
    This is a dashboard for simulating the intensity projection of a point source on a flat plane. 
    The intensity is calculated using the formula:
    $$
    I(x,y) = \\frac{I_0}{4 \pi r^2}
    $$
    where $I_0$ is the intensity at the source and $r$ is the distance from the source to the point $(x,y)$.
    """)
    st.image("assets/intensity_projection.png", width=400)

with st.expander("Constants"):
    PIXEL_PITCH = st.number_input("Pixel pitch (mm)", value=1.894, key="pixel_pitch")

col = st.columns(3)
with col[0]:
    height = st.number_input("Height of source (mm)", value=30.0, step=10.0)
with col[1]:
    colormap = st.selectbox("Colormap", ["jet", "viridis", "plasma", "inferno"])
with col[2]:
    add_grid = st.checkbox("Add grid", value=True)
    fixed_color_limits = st.checkbox("Fixed color limits")

def draw_grid_figure(pixel_pitch=st.session_state["pixel_pitch"], 
                     grid_size=11, fig=None, ax=None):
    
    
    if fig is None or ax is None:
        fig, ax = plt.subplots(figsize=(8, 8))

    # Calculate the offset to center the grid
    offset = (grid_size * pixel_pitch) / 2

    # Add squares to the axes
    for i in range(grid_size):
        for j in range(grid_size):
            x = (i * pixel_pitch) - offset
            y = (j * pixel_pitch) - offset
            square = patches.Rectangle(
                (x, y),
                pixel_pitch,
                pixel_pitch,
                edgecolor="black",
                facecolor="none",  # Set the facecolor to be transparent
                alpha=0.5,
                linewidth=2,  # Increase the edge thickness
            )
            ax.add_patch(square)

    # Set the aspect of the plot to be equal
    ax.set_aspect("equal")

    # Set limits
    # xy_limits = offset * 1.2
    # ax.set_xlim(-xy_limits, xy_limits)
    # ax.set_ylim(-xy_limits, xy_limits)

    return fig, ax


def relative_intensity(r, I0=1):
    """
    Calculates the relative intensity of a spherical wave source.
    """
    return I0 / (4 * math.pi * r**2)

def plot_intensity(H, fixed_clim=True, colormap_input="jet"):
    """
    Plots the projected intensity on a flat plane with 2D contour lines.
    """
    fig, ax = plt.subplots()
    # Define the range of x and y coordinates
    x = np.linspace(-15, 15, 101)
    y = np.linspace(-15, 15, 101)

    # Create a grid of x and y coordinates
    X, Y = np.meshgrid(x, y)

    # Calculate the relative intensity for each point on the grid
    O = np.sqrt(X**2 + Y**2)  # off-center distance
    R = np.sqrt(H**2 + O**2)
    I0 = 4 * math.pi * H**2
    Z = relative_intensity(R, I0=I0)

    # Plot the contour lines
    plt.contourf(X, Y, Z, levels=20, cmap=colormap_input, alpha=0.9)
    plt.colorbar()
    if fixed_clim:
        plt.clim(0, 1)  # Set the min and max values of the colorbar
    plt.xlabel("x (mm)")
    plt.ylabel("y (mm)")
    plt.title(f"Projected Intensity @ {H=}")
    return fig, ax


def plot_intensity_px(H, colormap_input="jet", fixed_clim=True):
    """
    Plots the projected intensity on a flat plane with filled contour lines.
    """
    x = np.linspace(-15, 15, 101)
    y = np.linspace(-15, 15, 101)

    X, Y = np.meshgrid(x, y)

    # Calculate the relative intensity for each point on the grid
    O = np.sqrt(X**2 + Y**2)  # off-center distance
    R = np.sqrt(H**2 + O**2)
    I0 = 4 * math.pi * H**2
    Z = relative_intensity(R, I0=I0)

    if fixed_clim:
        fig = go.Figure(
            data=go.Contour(
                z=Z,
                x=x,
                y=y,
                colorscale=colormap_input,
                contours=dict(start=0, end=1),
                hovertemplate="z: %{z:.2f}<extra></extra>"
            )
        )
    else:
        fig = go.Figure(
            data=go.Contour(
                z=Z,
                x=x,
                y=y,
                colorscale=colormap_input,
                hovertemplate="z: %{z:.2f}<extra></extra>"
            )
        )
        
    # add box with borders at x = -11, 11 and y = -11, 11
    fig.add_shape(
        type="rect",
        x0=-11,
        y0=-11,
        x1=11,
        y1=11,
        line=dict(
            color="black",
            width=2,
        ),
        fillcolor="rgba(0,0,0,0)", 
        opacity=0.5
    )
    
    return fig


fig, ax = plot_intensity(height, colormap_input=colormap, fixed_clim=fixed_color_limits)
if add_grid:
    fig, ax = draw_grid_figure(pixel_pitch=PIXEL_PITCH, fig=fig, ax=ax)
with st.expander("Matplotlib Figure", expanded=True):
    st.pyplot(fig)


fig = plot_intensity_px(height, colormap_input=colormap, fixed_clim=fixed_color_limits)
fig.update_layout(
    title=f"Projected Intensity @ {height=}",
    xaxis_title="x (mm)",
    yaxis_title="y (mm)",
    width=600,  # Update the width of the figure (in pixels)
    height=600,  # Update the height of the figure (in pixels)
)
with st.expander("Plotly Figure", expanded=False):
    st.plotly_chart(fig)