import streamlit as st

pages = [
    st.Page("st_pages/full_data_dashboard.py", title=" 📈 Full Data Dashboard",),
    # st.Page("st_pages/heatmap_spectrum.py", title=" 📊 Heatmap and Spectrum Analysis"),
    st.Page("st_pages/hole_projection.py", title=" 🔍 Hole Projection"),
    st.Page("st_pages/intensity_projection.py", title=" 💡 Intensity Projection"),
]

page = st.navigation(pages)

page.run()
