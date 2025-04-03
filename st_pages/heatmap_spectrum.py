import streamlit as st
import pandas as pd
import csv
import codecs

from data_handling_modules import TransformDf
from plotting_modules import (
    create_spectrum_average,
    create_spectrum_pixel,
    create_pixelized_heatmap,
)

st.set_page_config(
    "Heatmap and Spectrum Analysis",
    layout="wide",
    initial_sidebar_state="expanded",
)

from st_pages import Page, Section, show_pages, add_page_title, hide_pages

show_pages([
    Page("pages/full_data_dashboard.py", 
         "Full Data Dashboard", 
         ":chart_with_upwards_trend:"),
    Page("app.py", 
         "Heatmap and Spectrum Analysis", 
         "📚"),
    Page("pages/hole_projection.py",
            "Hole Projection",
            ":mag:"),
    Page("pages/intensity_projection.py",
            "Intensity Projection",
            ":bulb:"),
])

app_defaults = {
    "Am241": {
        "bin_peak": 95,
        "peak_halfwidth": 22,
        "max_bin": 199,
        "bin_range": (80, 125),
        "max_counts": 500,
    },
    "Co57": {
        "bin_peak": 243,
        "peak_halfwidth": 22,
        "max_bin": 300,
        "bin_range": (100, 300),
        "max_counts": 500,
    },
    "Cs137": {
        "bin_peak": 1800,
        "peak_halfwidth": 22,
        "max_bin": 1999,
        "bin_range": (1500, 1900),
        "max_counts": 500,
    },
}

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

color_scale = st.sidebar.selectbox(
    "Choose a color theme: ", ("Viridis", "Plasma", "Inferno", "Jet"),
)

reverse_color_theme = st.sidebar.checkbox("Reverse color theme")

if reverse_color_theme:
    color_scale = color_scale + "_r"

count_type = st.sidebar.radio(
    "Choose a count type: ", ("total_count", "peak_count",
                              "non_peak_count", "pixel_id")
)

normalize_check = st.sidebar.checkbox("Normalize heatmap")

col = st.columns([0.25, 0.25], gap="large")
with col[0]:
    source = st.radio(":radioactive_sign: Radiation Source", ("Am241", "Co57", "Cs137"))
with col[1]:
    bin_peak_input = st.number_input(
        "approximate bin peak", step=1, value=app_defaults[source]["bin_peak"]
    )
    peak_halfwidth_input = st.number_input(
        "peak halfwidth", value=app_defaults[source]["peak_halfwidth"], step=1
    )

# bin_peak_input = st.sidebar.number_input("Default bin peak", value=0, step=1, format="%d")
# bin_peak_input = int(bin_peak_input)


# peak_halfwidth_input = st.sidebar.slider(
#     "Peak halfwidth",
#     min_value=1,
#     max_value=50,
#     value=25,
#     key="peak_halfwidth_input",
# )

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

        # if no default bin peak is provided, use the filename to determine the radiation source and default bin peak
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
        
        if bin_peak_input != "":  # if a default bin peak is provided, override the previous value
            default_bin_peak = bin_peak_input
        elif bin_peak_input == "" and radiation_source == "Unknown":
            st.error("Please provide a valid bin peak for the uploaded file")
            raise Exception("Please provide a valid bin peak for the uploaded file")

        if uploaded_csv_file.type != "text/csv":
            st.error("Please upload a CSV file:")
            raise Exception("Please upload a CSV file")

        rows_to_skip = find_line_number(uploaded_csv_file, "H3D_Pixel") 
        if rows_to_skip is None: # try to find "Pixel" if "H3D_Pixel" is not found
            rows_to_skip = find_line_number(uploaded_csv_file, "Pixel")
            if rows_to_skip is None:
                st.error("Please upload a valid CSV file")
                raise Exception("Please upload a valid CSV file")
            
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
            
        TD = TransformDf()
        df = TD.transform_df(df)  # transform the data
        df = TD.add_peak_counts(df, bin_peak=bin_peak_input,
                                bin_width=peak_halfwidth_input)

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
                df, bin_peak=bin_peak_input, peak_halfwidth=peak_halfwidth_input
            )

            avg_spectrum_figure.update_layout(
                title=f"Average Spectrum of {radiation_source}"
            )

            st.plotly_chart(avg_spectrum_figure)

        with st.expander("HEATMAP and PIXEL SPECTRUM", expanded=True):
            columns = st.columns([1,1], gap="large")
            
            with columns[0]:
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

        # with st.expander("PIXEL SPECTRUM", expanded=False):
            with columns[1]:
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
                    bin_peak=bin_peak_input,
                    peak_halfwidth=peak_halfwidth_input,
                )
                pixel_spectrum_figure.update_layout(
                    title=f"Select Pixel Spectrum"
                )

                st.plotly_chart(pixel_spectrum_figure)

