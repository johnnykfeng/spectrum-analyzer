import streamlit as st
import pandas as pd
import csv
import codecs

from data_handling_modules import (TransformDf, ExtractModule)
from plotting_modules import (
    create_spectrum_average,
    create_spectrum_pixel,
    create_pixelized_heatmap,
)

st.set_page_config("Big Data Dashboard", page_icon="📊")


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

st.title("DEPRECATED Dashboard")

color_scale = st.sidebar.radio(
    "Choose a color theme: ", ("Viridis", "Plasma", "Inferno", "Jet")
)

reverse_color_theme = st.sidebar.checkbox("Reverse color theme")

if reverse_color_theme:
    color_scale = color_scale + "_r"

count_type = st.sidebar.radio(
    "Choose a count type: ", ("total_count", "peak_count",
                              "non_peak_count", "pixel_id")
)

normalize_check = st.sidebar.checkbox("Normalize heatmap")

bin_peak_input = st.sidebar.number_input("Default bin peak", step=1)

peak_halfwidth_input = st.sidebar.number_input("Default peak halfwidth", 
                                               value=50,
                                               step=1)

# uploaded_file = st.sidebar.file_uploader("Upload a CSV file", type=["csv", "xlsx"])
# # print the file path of the uploaded file
# if uploaded_file is not None:
#     st.write(uploaded_file.name)
#     st.write(uploaded_file.__dict__)

# input file path
file_path_input = st.text_input("Please enter the file path for excel or csv:", 
                                        value="R:\H3D-sensor-test\mask_sweep_2024-06-20_ALL_DATA\mask_sweep_2024-06-20.xlsx",
                                        key="file_path_input")

# file_path = r"R:\H3D-sensor-test\mask_sweep_2024-06-20_ALL_DATA\mask_sweep_2024-06-20.xlsx"
@st.cache_data
def parse_data(file_path_input):
    EM = ExtractModule(file_path_input)
    st.write(f"Number of lines in data file: {EM.count_lines()}")
    extracted_df_list = EM.extract_all_modules2df()

    TD = TransformDf()
    df_transformed_list = TD.transform_all_df(extracted_df_list)

    if bin_peak_input is not None and peak_halfwidth_input is not None:
        peak_halfwidth = peak_halfwidth_input
        df_transformed_list = TD.add_peak_counts_all(bin_peak_input, peak_halfwidth)

    x_positions = EM.extract_metadata_list(EM.csv_file, "stage_x_mm:")
    y_positions = EM.extract_metadata_list(EM.csv_file, "stage_y_mm:")
    heights = EM.extract_metadata_list(EM.csv_file, "height:")

    return (EM.number_of_modules, EM.n_pixels_x, EM.n_pixels_y, 
            x_positions, y_positions, heights, df_transformed_list)

N_MODULES, N_PIXELS_X, N_PIXELS_Y, x_positions, y_positions, heights, df_transformed_list = parse_data(file_path_input)

# create a slider to select the module
module_index = st.slider("Select a module:", 0, N_MODULES - 1, 0)

with st.expander("Average Spectrum", expanded=False):
    spectrum_avg_fig = create_spectrum_average(df_transformed_list[module_index], 
                                            bin_peak=bin_peak_input, 
                                            peak_halfwidth=peak_halfwidth_input)
    st.plotly_chart(spectrum_avg_fig)

with st.expander("Count Heatmap", expanded=False):
    heatmap_fig = create_pixelized_heatmap(df_transformed_list[module_index],
                                            count_type=count_type,
                                            normalization=normalize_check,
                                            color_scale=color_scale)
    st.plotly_chart(heatmap_fig)

    
    

