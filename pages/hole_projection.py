import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

st.title("Hole Projections")

with st.expander("Constants"):
    PIXEL_PITCH = st.number_input("Pixel pitch (mm)", value=1.894)
    HOLE_DIAMETER = st.number_input("Mask hole diameter (mm)", value=0.75)
    
cols = st.columns(3)

with cols[0]:
    H = st.number_input("H (mm), height from source from mask",
                        min_value=0.0, max_value=None, step=10.0,
                        value=180.0)

    h = st.number_input("h (mm), height from mask to detector",
                        min_value=0.0, max_value=None, step=1.0, 
                        value=22.0)
    
with cols[1]:
    source_x = st.number_input("Source x (mm)", value=0.0, step=0.5)
    sourcy_y = st.number_input("Source y (mm)", value=0.0, step=0.5)
    POINT_SOURCE = (source_x, sourcy_y)
    
with cols[2]:
    mask_x = st.number_input("Mask x (mm)", value=0.0, step=PIXEL_PITCH)
    mask_y = st.number_input("Mask y (mm)", value=0.0, step=PIXEL_PITCH)
    MASK_POSITION = (mask_x, mask_y)

def mask_hole_positions(HOLE_PITCH, MASK_OFFSET_X, MASK_OFFSET_Y):
    x_positions = np.arange(-1.5*HOLE_PITCH+MASK_OFFSET_X,
                            1.6*HOLE_PITCH+MASK_OFFSET_X,
                            HOLE_PITCH)
    y_positions = np.arange(1.5*HOLE_PITCH+MASK_OFFSET_Y,
                            -1.6*HOLE_PITCH+MASK_OFFSET_Y,
                            -HOLE_PITCH)
    x_mesh, y_mesh = np.meshgrid(x_positions, y_positions)
    hole_positions = np.stack((x_mesh, y_mesh), axis=-1)
    return hole_positions, x_mesh, y_mesh

def projection(h, H, POINT_SOURCE, MASK_POSITIrON, 
               PIXEL_PITCH=1.894, HOLE_DIAMETER=0.75):
    hole_positions, x_mesh, y_mesh = mask_hole_positions(
        3*PIXEL_PITCH, MASK_POSITION[0], MASK_POSITION[1])

    x_distances = x_mesh - POINT_SOURCE[0]
    y_distances = y_mesh - POINT_SOURCE[1]
    x_shifts = x_distances * h / H
    y_shifts = y_distances * h / H

    x_projected = x_mesh + x_shifts
    y_projected = y_mesh + y_shifts

    diameters = np.ones_like(x_mesh) * HOLE_DIAMETER * (1 + h / H)

    # diagonals = np.linalg.norm(hole_positions - POINT_SOURCE, axis=-1)
    # diagonal_shifts = diagonals * h / H
    return x_projected, y_projected, diameters

def draw_grid_figure(PIXEL_PITCH=1.894, GRID_SIZE=11):
    # Create a figure and an axes
    fig, ax = plt.subplots(figsize=(8, 8))

    # Calculate the offset to center the grid
    offset = (GRID_SIZE * PIXEL_PITCH) / 2

    # Add squares to the axes
    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            x = (i * PIXEL_PITCH) - offset
            y = (j * PIXEL_PITCH) - offset
            square = patches.Rectangle(
                (x, y),
                PIXEL_PITCH,
                PIXEL_PITCH,
                edgecolor="black",
                facecolor="gold",
                alpha=0.5,
                linewidth=2,  # Increase the edge thickness
            )
            ax.add_patch(square)

    # Set the aspect of the plot to be equal
    ax.set_aspect("equal")

    # Set limits
    xy_limits = offset * 1.2
    ax.set_xlim(-xy_limits, xy_limits)
    ax.set_ylim(-xy_limits, xy_limits)
    
    return fig, ax

hole_positions, x_mesh, y_mesh = mask_hole_positions(3*PIXEL_PITCH, MASK_POSITION[0], MASK_POSITION[1])
x_projected, y_projected, diameters = projection(h, H, POINT_SOURCE, MASK_POSITION)

fig, ax = draw_grid_figure(PIXEL_PITCH=1.894, GRID_SIZE=11)

ax.plot([POINT_SOURCE[0]], [POINT_SOURCE[1]], color="red", marker="x", markersize=10)

for x_mesh_i, y_mesh_i in zip(x_mesh.flatten(), y_mesh.flatten()):
    circle = plt.Circle((x_mesh_i, y_mesh_i), 
                        HOLE_DIAMETER / 2, 
                        color="blue", fill=True, alpha=0.5)
    plt.gca().add_artist(circle)

for x_projected_i, y_projected_i, di in zip(x_projected.flatten(), y_projected.flatten(), diameters.flatten()):
    circle = plt.Circle((x_projected_i, y_projected_i), 
                        di / 2, 
                        color="red", fill=True, alpha=0.5)
    plt.gca().add_artist(circle)

ax.grid(alpha=0.6)
ax.set_title("Projection of mask holes")
ax.set_xlabel("x (mm)")
ax.set_ylabel("y (mm)")

st.pyplot(fig)