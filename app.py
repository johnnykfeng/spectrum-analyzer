import streamlit as st
import pandas as pd
import sys
import os
import plotly.express as px
import numpy as np
import csv
import codecs
import plotly.graph_objects as go

from data_handling_modules import TransformDf
from plotting_modules import (
    create_spectrum_average,
    create_spectrum_pixel,
    create_pixelized_heatmap,
)


# HELPER FUNCTIONS
def find_line_number(csv_file, target_string):
    """Find the line number where the target string is found in the csv file.
    Used to determine the number of rows to skip when reading the csv file.
    """
    text_io = codecs.getreader("utf-8")(csv_file)
    reader = csv.reader(text_io)
    for row_index, row in enumerate(reader):
        for cell in row:
            if target_string in cell:
                return row_index

def pixel_selectbox(axis, col_index, csv_index):
    return st.selectbox(
                label=f"{axis}-index-{col_index}:",
                options=(1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11),
                index=col_index,
                key=f"{axis}_index_{col_index}_{csv_index}"
                )
    
@st.cache_data
def convert_df_to_csv(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    df_download = df.drop(columns=['array_bins'])
    return df_download.to_csv().encode("utf-8")

st.title("Heatmap and Spectrum Analysis")

uploaded_csv_file1, uploaded_csv_file2, uploaded_csv_file3 = None, None, None
if (
    uploaded_csv_file1 is None
    and uploaded_csv_file2 is None
    and uploaded_csv_file3 is None
):
    st.subheader("Upload proper CSV file at the sidebar to get started.")

color_scale = st.sidebar.radio(
    "Choose a color theme: ", ("Viridis", "Plasma", "Inferno", "Jet")
)

reverse_color_theme = st.sidebar.checkbox("Reverse color theme")

count_type = st.sidebar.radio(
    "Choose a count type: ", ("total_count", "peak_count",
                              "non_peak_count", "pixel_id")
)

normalize_check = st.sidebar.checkbox("Normalize heatmap")

if reverse_color_theme:
    color_scale = color_scale + "_r"

uploaded_csv_file1 = st.sidebar.file_uploader(
    "Please upload a CSV file:", type="csv", key="fileUploader1"
)

uploaded_csv_file2 = st.sidebar.file_uploader(
    "Please upload a CSV file:", type="csv", key="fileUploader2"
)

uploaded_csv_file3 = st.sidebar.file_uploader(
    "Please upload a CSV file:", type="csv", key="fileUploader3"
)

# Process each uploaded file
for csv_index, uploaded_csv_file in enumerate(
    [uploaded_csv_file1, uploaded_csv_file2, uploaded_csv_file3]
):
    if uploaded_csv_file is not None:
        filename = uploaded_csv_file.name
        filename = (
            filename.lower()
        )  # convert to lowercase for case-insensitive comparison
        if filename.endswith("am241.csv"):
            default_bin_peak = "96"
            radiation_source = "Am241"
        elif filename.endswith("cs137.csv"):
            filename_no_ext = filename.replace(".csv", "")
            if "co57" in filename_no_ext.lower():
                default_bin_peak = "244"
                radiation_source = "Co57"
            elif "cs137" in filename_no_ext.lower():
                default_bin_peak = "1558"
                radiation_source = "Cs137"
            
        else:
            radiation_source = "Unknown"
            default_bin_peak = ""

        if uploaded_csv_file.type != "text/csv":
            st.error("Please upload a CSV file:")
            raise Exception("Please upload a CSV file")

        rows_to_skip = find_line_number(uploaded_csv_file, "H3D_Pixel")
        uploaded_csv_file.seek(0)  # reset the file pointer to the beginning
        
        st.divider()
        st.subheader(f"Uploaded: {uploaded_csv_file.name}")

        with st.expander("Show file details"):
            st.write(f"{uploaded_csv_file.name = }")
            st.write(f"{uploaded_csv_file.type = }")
            st.write(f"{type(uploaded_csv_file) = }")
            st.warning(f"{rows_to_skip = }")
            st.success(f"Radiation source: {radiation_source}")
            st.info(f"Default bin peak: {default_bin_peak}")

        # Read the CSV file
        df = pd.read_csv(
            uploaded_csv_file,
            skiprows=rows_to_skip,
            nrows=121,
            index_col="H3D_Pixel",
            header=0,
        )

        with st.expander("Show the original csv data"):
            st.dataframe(df)  # display original csv data

        col1, col2 = st.columns(2)
        with col1:
            # must have two different sliders for bin width (streamlit needs unique key)
            peak_halfwidth = st.slider(
                "Peak halfwidth",
                min_value=1,
                max_value=50,
                value=25,
                key=f"bin_width_{csv_index}",
            )
        with col2:
            bin_peak = st.text_input(
                "Bin peak", value=default_bin_peak, key=f"bin_peak_{csv_index}"
            )
            bin_peak = int(bin_peak) if bin_peak else None

        TD = TransformDf()
        df = TD.transform_df(df)  # transform the data
        df = TD.add_peak_counts(df, bin_peak=bin_peak,
                                bin_width=peak_halfwidth)

        csv_file_downloadable = convert_df_to_csv(df)
        with st.expander("Show the transformed csv data"):
            st.dataframe(df)
            st.download_button(
                label="Download transformed data",
                data=csv_file_downloadable,
                file_name="transformed.csv",
                mime="text/csv",
                key=f"download_button_{csv_index}",
            )

        with st.expander("AVERAGE SPECTRUM", expanded=True):
            avg_spectrum_figure = create_spectrum_average(
                df, bin_peak=bin_peak, peak_halfwidth=peak_halfwidth
            )

            avg_spectrum_figure.update_layout(
                title=f"Average Spectrum of {radiation_source}"
            )

            st.plotly_chart(avg_spectrum_figure)

        with st.expander("HEATMAP", expanded=True):
            count_table = df.pivot_table(
                index="y_index", columns="x_index", values=count_type
            )

            color_range = st.slider(
                label="Color Range Slider: ",
                min_value=0,  # min is 0
                max_value=int(count_table.max().max()),
                value=( # default range
                    int(count_table.min().min()),
                    int(count_table.max().max()),
                ),  
                step=5,
                key=f"color_range_{csv_index}",
            )

            
            if normalize_check == True:
                max_pixel_value = count_table.values.max()
                count_table = (count_table / max_pixel_value).round(2)

                # color range slider
                color_range = st.slider(
                    label="Color Range Slider: ",
                    min_value=0.0,  # min is 0
                    max_value=float(count_table.max().max()),
                    value=( # default range
                        float(count_table.min().min()),
                        float(count_table.max().max()),
                    ),  
                    step=0.1,
                    key=f"color_range_normalized_{csv_index}",
                )

            heatmap_fig = create_pixelized_heatmap(
                df,
                count_type,
                normalization=normalize_check,
                color_scale=color_scale,
                color_range=color_range,
            )

            heatmap_fig.update_layout(
                title=f"Heatmap of {uploaded_csv_file.name}")

            st.plotly_chart(heatmap_fig)

        with st.expander("PIXEL SPECTRUM", expanded=False):

            num_pixels = st.number_input("Number of pixels to display", 
                                         min_value=1, 
                                         max_value=10, 
                                         value=4,
                                         key=f"num_pixels_{csv_index}")
            pixel_indices = []
            for c, column in enumerate(st.columns(num_pixels)):
                with column:
                    x_index = pixel_selectbox('X', c, csv_index)
                    y_index = pixel_selectbox('Y', c, csv_index)
                    pixel_indices.append((x_index, y_index))

            pixel_spectrum_figure = create_spectrum_pixel(
                df,
                *pixel_indices,
                bin_peak=bin_peak,
                peak_halfwidth=peak_halfwidth,
            )
            pixel_spectrum_figure.update_layout(
                title=f"Select Pixel Spectrum"
            )

            st.plotly_chart(pixel_spectrum_figure)

