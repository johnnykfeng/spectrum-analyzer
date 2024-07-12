# import streamlit as st
import math


def divergence_angle(H, b):
    half_angle = math.degrees(math.atan(b*0.5 / H))
    return round(2*half_angle, 2)

def displacement(angle, h):
    return round(h * math.tan(math.radians(angle)), 2)


if __name__ == '__main__':
    H = 180 # mm
    b = 0.75 # mm
    angle = divergence_angle(H, b)
    print(f"{divergence_angle(H, b) = } degrees")
    h = 22
    D = displacement(angle/2, h)
    print(f"{displacement(angle/2, h) = } mm")
    
    

