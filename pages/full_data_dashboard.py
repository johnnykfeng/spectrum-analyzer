import streamlit as st

from data_handling_modules import TransformDf, ExtractModule, ExtractModuleStreamlit

from plotting_modules import (
    create_spectrum_average,
    create_spectrum_pixel,
    create_pixelized_heatmap,
    create_spectrum_pixel_sweep,
    create_count_sweep
)

st.set_page_config("Full Data Dashboard", page_icon="📊",
                   layout="wide", initial_sidebar_state="expanded")


@st.cache_data
def convert_df_to_csv(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    df_download = df.drop(columns=["array_bins"])
    return df_download.to_csv().encode("utf-8")


st.title("Full Data Dashboard")


color_scale = st.sidebar.radio(
    "Choose a color theme: ", ("Viridis", "Plasma", "Inferno", "Jet")
)

reverse_color_theme = st.sidebar.checkbox("Reverse color theme")

if reverse_color_theme:
    color_scale = color_scale + "_r"

count_type = st.sidebar.radio(
    "Choose a count type: ", ("total_count", "peak_count", "non_peak_count", "pixel_id")
)

normalize_check = st.sidebar.checkbox("Normalize heatmap")

bin_peak_input = st.sidebar.number_input("Default bin peak", step=1, value=95)

peak_halfwidth_input = st.sidebar.number_input(
    "Default peak halfwidth", value=50, step=1
)

st.warning("Only File uploader is working for now")
upload_type = st.radio("File upload type", ("File uploader", "Directory input"))
if upload_type == "File uploader":
    uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])
else:
    file_path_input = st.text_input(
        "Please enter the file path for excel or csv:",
        value="R:\H3D-sensor-test\mask_sweep_2024-06-20_ALL_DATA\mask_sweep_2024-06-20.csv",
        key="file_path_input",
    )


@st.cache_data
def parse_uploaded_file(uploaded_file, bin_peak_input, peak_halfwidth, modules_to_skip=0):
    st.write(uploaded_file.name)
    EM = ExtractModuleStreamlit(uploaded_file)

    extracted_df_list = EM.extract_all_modules2df()
    extracted_df_list = extracted_df_list[modules_to_skip:]
    N_MODULES = EM.number_of_modules - modules_to_skip
    # if not include_background:
    #     extracted_df_list = extracted_df_list[1:]
    #     N_MODULES = EM.number_of_modules - 1
    # else:
    #     N_MODULES = EM.number_of_modules

    TD = TransformDf()
    df_transformed_list = TD.transform_all_df(extracted_df_list)
    if bin_peak_input is not None and peak_halfwidth_input is not None:
        peak_halfwidth = peak_halfwidth_input
        df_transformed_list = TD.add_peak_counts_all(bin_peak_input, peak_halfwidth)

    # x_positions = EM.extract_metadata_list(EM.csv_file, "stage_x_mm:")
    # y_positions = EM.extract_metadata_list(EM.csv_file, "stage_y_mm:")
    x_positions = EM.extract_metadata_list(EM.csv_file, "stage_x_px:")
    y_positions = EM.extract_metadata_list(EM.csv_file, "stage_y_px:")
    x_positions = [float(x) for x in x_positions] # convert list of str to float
    y_positions = [float(y) for y in y_positions] # convert list of str to float
    heights = EM.extract_metadata_list(EM.csv_file, "height:")
    # st.write(x_positions, y_positions, heights)

    return (
        N_MODULES,
        EM.n_pixels_x,
        EM.n_pixels_y,
        x_positions,
        y_positions,
        heights,
        df_transformed_list,
    )


def pixel_selectbox(axis, col_index, csv_index, default_index=1):
    return st.selectbox(
        label=f"{axis}-index-{col_index}:",
        options=(1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11),
        index=default_index - 1,
        key=f"{axis}_index_{col_index}_{csv_index}",
    )


if "pixel_indices" not in st.session_state:
    st.session_state.pixel_indices = []
# st.write("Session State Pixel indices")
# st.write(*st.session_state.pixel_indices)

if "num_pixels" not in st.session_state:
    st.session_state.num_pixels = 2

if "counts_max_pixel" not in st.session_state:
    st.session_state.counts_max_pixel = 15

if uploaded_file is not None:
    (
        N_MODULES,
        N_PIXELS_X,
        N_PIXELS_Y,
        x_positions,
        y_positions,
        heights,
        df_transformed_list,
    ) = parse_uploaded_file(uploaded_file, bin_peak_input, peak_halfwidth_input, modules_to_skip=0)

    with st.expander("Data Info", expanded=False):
        st.write(f"Number of modules: {N_MODULES}")
        st.write(f"Stage X position: {x_positions}")
        st.write(f"Stage Y position: {y_positions}")
        st.write(f"Height: {heights}")

    # create a slider to select the module
    # module_index = st.sidebar.slider("Select a module:", 0, N_MODULES - 1, 0)

    with st.expander("HEATMAP and PIXEL SPECTRUM", expanded=True):
        relative_x_positions = [round(x-x_positions[1], 2) for x in x_positions]
        relative_y_positions = [round(y-y_positions[1], 2) for y in y_positions]

        plot_columns = st.columns([1, 1])
        
        with plot_columns[0]:
            # create a slider to select the module
            module_index = st.slider("Select a module:", 0, N_MODULES - 1, 0)
            heatmap_fig = create_pixelized_heatmap(
                df_transformed_list[module_index],
                count_type=count_type,
                normalization=normalize_check,
                color_scale=color_scale,
            )
            heatmap_fig.update_layout(title=f"X-stage: {relative_x_positions[module_index]} px,  Y-stage: {relative_y_positions[module_index]} px")
            st.plotly_chart(heatmap_fig)
            
            
        with plot_columns[1]:
            
            num_pixels = st.number_input(
                "Number of pixels to display",
                min_value=1,
                max_value=10,
                value=st.session_state.num_pixels,
                key=f"num_pixels_{module_index}",
            )
            st.session_state.num_pixels = num_pixels

            pixel_selections = []
            for c, column in enumerate(st.columns(num_pixels)):
                with column:
                    # check if st.session_state.pixel_indices is not empty
                    if st.session_state.pixel_indices != [] and c < len(
                        st.session_state.pixel_indices
                    ):
                        # last_x_index = st.session_state.pixel_indices[c][0]
                        # last_y_index = st.session_state.pixel_indices[c][1]
                        x_index = pixel_selectbox("X", c, module_index, st.session_state.pixel_indices[c][0])
                        y_index = pixel_selectbox("Y", c, module_index, st.session_state.pixel_indices[c][1])
                    else:
                        x_index = pixel_selectbox("X", c, module_index)
                        y_index = pixel_selectbox("Y", c, module_index)
                    pixel_selections.append((x_index, y_index))

            st.session_state.pixel_indices = pixel_selections
            

            
            sub_columns = st.columns([4, 1], gap="large")
            with sub_columns[0]:
                range_slider = st.slider(
                    "range slider (bins)",
                    min_value=0,
                    max_value=199 ,
                    value=(80,120),
                    step=1,)
            with sub_columns[1]:
                # last_counts_max_pixel = st.session_state.counts_max_pixel
                st.session_state.counts_max_pixel = st.number_input("Max Counts", 
                                                   value=st.session_state.counts_max_pixel, step=1,
                                                    key=f"y_max_{module_index}")
                    

            pixel_spectrum_figure = create_spectrum_pixel(
                df_transformed_list[module_index],
                *st.session_state.pixel_indices,
                bin_peak=bin_peak_input,
                peak_halfwidth=peak_halfwidth_input,
                x_range=range_slider,
                y_range=[0, st.session_state.counts_max_pixel],
            )
            pixel_spectrum_figure.update_layout(title="Select Pixel Spectrum")
            
            st.plotly_chart(pixel_spectrum_figure)

    with st.expander("Average Spectrum", expanded=False):
        spectrum_avg_fig = create_spectrum_average(
            df_transformed_list[module_index],
            bin_peak=bin_peak_input,
            peak_halfwidth=peak_halfwidth_input,
        )
        st.plotly_chart(spectrum_avg_fig)

    with st.expander("Sweep analysis", expanded=True):
        # st.write(f"Stage X position: {x_positions}")
        # st.write(f"Stage Y position: {y_positions}")
        # st.write(f"Height: {heights}")
        relative_x_positions = [round(x-x_positions[1], 2) for x in x_positions]
        data_range = st.slider(
            "Modules to include:",
            min_value=0,
            max_value=N_MODULES ,
            value=(1, N_MODULES ),
            step=1,
        )
        columns = st.columns([1, 1], gap="large")
        with columns[0]:
            sub_columns = st.columns([3, 1])
            with sub_columns[0]:
                range_slider_x = st.slider(
                    "X-range slider (bins)",
                    min_value=0,
                    max_value=199 ,
                    value=(80,120),
                    step=1,
                    key="range_slider_x",)
            with sub_columns[1]:
                y_max = st.number_input("Max Counts", value=500, step=1)
            
            # x_choice = pixel_selectbox("X", "Pixel", 101)
        with columns[1]:
            sub_columns = st.columns([1, 1])
            with sub_columns[0]:
                x_choice = pixel_selectbox("X", "Pixel", 101)
            with sub_columns[1]:
                y_choice = pixel_selectbox("Y", "Pixel", 102)
            
        spectrum_sweep = create_spectrum_pixel_sweep(
            df_transformed_list,
            x_index=x_choice,
            y_index=y_choice,
            min_data_range=data_range[0],
            max_data_range=data_range[1],
            x_range=range_slider_x,
            y_range=[0, y_max],
            stage_x_mm=relative_x_positions,
        )
        with columns[0]:
            st.plotly_chart(spectrum_sweep)
        
        count_sweep = create_count_sweep(
            df_transformed_list,
            count_type=count_type,
            x_index=x_choice,
            y_index=y_choice,
            min_data_range=data_range[0],
            max_data_range=data_range[1],
            x_range=[75, 125],
            y_range=[0, 120],
            stage_x_mm=relative_x_positions,
        )
        count_sweep.update_layout(xaxis_title="Relative Stage X (mm)")
        with columns[1]:
            st.plotly_chart(count_sweep)
