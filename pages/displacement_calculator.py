import streamlit as st
import math

PIXEL_PITCH = 1.894  # mm
HOLE_DIAMETER = 0.75 # mm
st.title("Displacement Calculator")
st.write("This app calculates the displacement of the illumination spot on the detector.")
with st.sidebar:
    st.subheader("Constants:")
    st.info(f"Pixel pitch = {PIXEL_PITCH} mm  \nHole diameter = {HOLE_DIAMETER} mm")

def divergence_angle(H, b):
    half_angle = math.degrees(math.atan(b*0.5 / H))
    return 2*half_angle


def displacement(angle, h):
    return h * math.tan(math.radians(angle))

def spot_diameter(H, h, hole_size=HOLE_DIAMETER):
    angle = divergence_angle(H, HOLE_DIAMETER)
    d = displacement(angle, h)
    spot_diameter = 2 * d + HOLE_DIAMETER
    return spot_diameter
    
H = st.number_input("H (mm), height of source from mask",
                    min_value=0.0, max_value=None, step=10.0,
                    value=180.0)

b = st.number_input("b (mm), furthest distance between holes",
                    min_value=0.0, max_value=None, step=1.0, 
                    value=3*PIXEL_PITCH)

full_angle = divergence_angle(H, b)

h = st.number_input("h (mm), distance from mask to detector",
                    min_value=0.0, max_value=None, step=1.0, 
                    value=22.0)

d = displacement(full_angle, h)

st.subheader("Results:")
st.success(f"Full divergence angle: = {full_angle:.2f} degrees")
st.success(f"Displacement = {d:.2f} mm or {d/PIXEL_PITCH:.2f} pixels")
# st.success(f"Displacement in pixels: {d/PIXEL_PITCH:.2f} pixels")
st.success(f"Illumination spot diameter = {spot_diameter(H, h):.2f} mm")

# if __name__ == '__main__':
#     H = 180  # mm
#     b = 0.75  # mm
#     angle = divergence_angle(H, b)
#     print(f"{divergence_angle(H, b) = } degrees")
#     h = 22
#     D = displacement(angle/2, h)
#     print(f"{displacement(angle/2, h) = } mm")
