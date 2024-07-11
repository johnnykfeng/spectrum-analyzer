import streamlit as st

from data_handling_modules import TransformDf, ExtractModule, ExtractModuleStreamlit

from plotting_modules import (
    create_spectrum_average,
    create_spectrum_pixel,
    create_pixelized_heatmap,
    create_spectrum_pixel_sweep,
    create_count_sweep,
)

st.set_page_config(
    "Full Data Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_data
def convert_df_to_csv(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    df_download = df.drop(columns=["array_bins"])
    return df_download.to_csv().encode("utf-8")

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

st.title(":chart_with_upwards_trend: Full Data Dashboard")


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

# st.warning("Only File uploader is working for now")
col = st.columns([0.25, 0.25, 0.5], gap="large")
with col[0]:
    source = st.radio(":radioactive_sign: Radiation Source", ("Am241", "Co57", "Cs137"))
with col[1]:
    bin_peak_input = st.number_input(
        "approximate bin peak", step=1, value=app_defaults[source]["bin_peak"]
    )
    peak_halfwidth_input = st.number_input(
        "peak halfwidth", value=app_defaults[source]["peak_halfwidth"], step=1
    )

with col[2]:
    uploaded_file = st.file_uploader("Upload a CSV file 💾", type=["csv"])


@st.cache_data
def parse_uploaded_file(
    uploaded_file, bin_peak_input, peak_halfwidth, modules_to_skip=0
):
    st.write(uploaded_file.name)
    EM = ExtractModuleStreamlit(uploaded_file)

    extracted_df_list = EM.extract_all_modules2df()
    extracted_df_list = extracted_df_list[modules_to_skip:]
    N_MODULES = EM.number_of_modules - modules_to_skip

    TD = TransformDf()
    df_transformed_list = TD.transform_all_df(extracted_df_list)
    if bin_peak_input is not None and peak_halfwidth_input is not None:
        peak_halfwidth = peak_halfwidth_input
        df_transformed_list = TD.add_peak_counts_all(bin_peak_input, peak_halfwidth)
        df_transformed_list = TD.add_bin_max_all(bin_peak_input, peak_halfwidth)

    x_positions_mm = EM.extract_metadata_list(EM.csv_file, "stage_x_mm:")
    y_positions_mm = EM.extract_metadata_list(EM.csv_file, "stage_y_mm:")
    x_positions = EM.extract_metadata_list(EM.csv_file, "stage_x_px:")
    y_positions = EM.extract_metadata_list(EM.csv_file, "stage_y_px:")
    x_positions = [float(x) for x in x_positions]  # convert list of str to float
    y_positions = [float(y) for y in y_positions]  # convert list of str to float
    heights = EM.extract_metadata_list(EM.csv_file, "height:")
    # st.write(x_positions, y_positions, heights)

    return (
        N_MODULES,
        EM.n_pixels_x,
        EM.n_pixels_y,
        x_positions,
        y_positions,
        x_positions_mm,
        y_positions_mm,
        heights,
        df_transformed_list,
    )


def pixel_selectbox(axis, col_index, module_index, key_str, default_index=1):
    """
    axis: str, x or y
    col_index: int, number of pixels to create
    module_index: int"""
    return st.selectbox(
        label=f"{axis}-index-{col_index}:",
        options=(1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11),
        index=default_index - 1,
        key=f"{key_str}_{axis}_index_{col_index}_{module_index}",
    )


# use session_state to store default values of widgets
if "pixel_indices" not in st.session_state:
    st.session_state.pixel_indices = []

if "pixel_indices_sweep" not in st.session_state:
    st.session_state.pixel_indices_sweep = []

if "num_pixels" not in st.session_state:
    st.session_state.num_pixels = 2

if "num_pixels_sweep" not in st.session_state:
    st.session_state.num_pixels_sweep = 4

if "counts_max_pixel" not in st.session_state:
    st.session_state.counts_max_pixel = app_defaults[source]["max_counts"]

if uploaded_file is not None:
    (
        N_MODULES,
        N_PIXELS_X,
        N_PIXELS_Y,
        x_positions,
        y_positions,
        x_positions_mm,
        y_positions_mm,
        heights,
        df_transformed_list,
    ) = parse_uploaded_file(
        uploaded_file, bin_peak_input, peak_halfwidth_input, modules_to_skip=0
    )

    with st.expander("Data Info", expanded=False):
        st.write(f"Number of modules: {N_MODULES}")
        st.write(f"Stage X position: {x_positions}")
        st.write(f"Stage Y position: {y_positions}")
        st.write(f"Height: {heights}")
        st.write(df_transformed_list[1])

    # create a slider to select the module
    # module_index = st.sidebar.slider("Select a module:", 0, N_MODULES - 1, 0)

    with st.expander("HEATMAP and PIXEL SPECTRUM", expanded=True):
        relative_x_positions = [round(x - x_positions[1], 2) for x in x_positions]
        relative_y_positions = [round(y - y_positions[1], 2) for y in y_positions]

        heatmap_panel, pixel_spectrum_panel = st.columns([1, 1])

        with heatmap_panel:
            # create a slider to select the module
            module_index = st.slider("Select a module:", 0, N_MODULES - 1, 0)
            heatmap_fig = create_pixelized_heatmap(
                df_transformed_list[module_index],
                count_type=count_type,
                normalization=normalize_check,
                color_scale=color_scale,
            )

            st.write(f"X: {x_positions_mm[module_index]} mm,  Y: {y_positions_mm[module_index]} mm")
            heatmap_fig.update_layout(
                title=f"X-stage: {relative_x_positions[module_index]} px,  Y-stage: {relative_y_positions[module_index]} px"
            )
            st.plotly_chart(heatmap_fig)

        with pixel_spectrum_panel:
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
                        x_index = pixel_selectbox(
                            "X", c, module_index, "spectrum", st.session_state.pixel_indices[c][0], 
                        )
                        y_index = pixel_selectbox(
                            "Y", c, module_index, "spectrum", st.session_state.pixel_indices[c][1]
                        )
                    else:
                        x_index = pixel_selectbox("X", c, module_index, "spectrum")
                        y_index = pixel_selectbox("Y", c, module_index, "spectrum")
                    pixel_selections.append((x_index, y_index))

            st.session_state.pixel_indices = pixel_selections

            sub_columns = st.columns([4, 1], gap="large")
            with sub_columns[0]:
                range_slider = st.slider(
                    "range slider (bins)",
                    min_value=0,
                    max_value=app_defaults[source]["max_bin"],
                    value=app_defaults[source]["bin_range"],
                    step=1,
                )
            with sub_columns[1]:
                # last_counts_max_pixel = st.session_state.counts_max_pixel
                st.session_state.counts_max_pixel = st.number_input(
                    "Max Counts",
                    value=st.session_state.counts_max_pixel,
                    step=1,
                    key=f"y_max_pixel_select",
                )

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
            x_range=[0, app_defaults[source]["max_bin"]],
            y_range=[0, app_defaults[source]["max_counts"]],
        )
        st.plotly_chart(spectrum_avg_fig)


    axes_choice = st.radio(
        "sweep axis",
        ("X-abs", "Y-abs", "X-relative", "Y-relative"),
        horizontal=True,
        key="axes_choice",
    )


    with st.expander("SWEEP ANALYSIS", expanded=True):
        relative_x_positions = [round(x - x_positions[1], 2) for x in x_positions]
        relative_y_positions = [round(y - y_positions[1], 2) for y in y_positions]
        x_values = {
            "X-abs": x_positions,
            "Y-abs": y_positions,
            "X-relative": relative_x_positions,
            "Y-relative": relative_y_positions,
        }

        sub_columns = st.columns([0.35, 0.65], gap="large")
        pixel_selections = []

        # placeholder = st.container()

        with sub_columns[0]:
            subsub_columns = st.columns([1, 1])
            with subsub_columns[0]:
                x_choice = pixel_selectbox("X", "Pixel", 101, "sweep")
            with subsub_columns[1]:
                y_choice = pixel_selectbox("Y", "Pixel", 102, "sweep")
            pixel_selections.append((x_choice, y_choice))
        with sub_columns[1]:
            data_range = st.slider(
                "Modules to include:",
                min_value=0,
                max_value=N_MODULES,
                value=(1, N_MODULES),
                step=1,
            )

        # with placeholder:
        left_panel, right_panel = st.columns([1, 1], gap="large")
        with left_panel:
            sub_columns = st.columns([3, 1], gap="large")
            with sub_columns[0]:
                range_slider_x = st.slider(
                    "X-range slider (bins)",
                    min_value=0,
                    max_value=app_defaults[source]["max_bin"],
                    value=app_defaults[source]["bin_range"],
                    step=1,
                    key="range_slider_x",
                )
            with sub_columns[1]:
                y_max = st.number_input(
                    "Max Counts",
                    value=app_defaults[source]["max_counts"],
                    step=1,
                    key="y_max_sweep",
                )

        with right_panel:
            count_sweep_plot_placeholder = st.empty()
        with left_panel:
            spectrum_sweep = create_spectrum_pixel_sweep(
                df_transformed_list,
                x_choice,
                y_choice,
                data_range[0],
                data_range[1],
                x_values[axes_choice],
                x_range=range_slider_x,
                y_range=[0, y_max],
            )
            st.plotly_chart(spectrum_sweep)

        # with right_panel:
        count_sweep = create_count_sweep(
            df_transformed_list,
            count_type,
            data_range[0],
            data_range[1],
            x_values[axes_choice],
            *pixel_selections,
        )
        count_sweep.update_layout(xaxis_title=f"{axes_choice} Stage Position (px)")
        count_sweep_plot_placeholder.plotly_chart(count_sweep)

    with st.expander("SWEEP MULTIPLE PIXELS", expanded=True):
        num_pixels = st.number_input(
            "Number of pixels to display",
            min_value=1,
            max_value=10,
            value=st.session_state.num_pixels_sweep,
            key=f"num_pixels_sweep_key",
        )
        st.session_state.num_pixels_sweep = num_pixels

        pixel_selections = []
        for c, column in enumerate(st.columns(num_pixels)):
            with column:
                # check if st.session_state.pixel_indices is not empty
                if st.session_state.pixel_indices != [] and c < len(
                    st.session_state.pixel_indices
                ):
                    x_index = pixel_selectbox(
                        "X", c, 101, "counts_sweep", st.session_state.pixel_indices[c][0]
                    )
                    y_index = pixel_selectbox(
                        "Y", c, 102, "counts_sweep", st.session_state.pixel_indices[c][1]
                    )
                else:
                    x_index = pixel_selectbox("X", c, 101, "counts_sweep")
                    y_index = pixel_selectbox("Y", c, 102, "counts_sweep")
                pixel_selections.append((x_index, y_index))

        st.session_state.pixel_indices_sweep = pixel_selections

        cols = st.columns([0.35, 0.65], gap="large")
        with cols[0]:
            include_summed_counts = st.checkbox("Include summed counts", value=True)
        with cols[1]:
            data_range_2 = st.slider(
                "Modules to include:",
                min_value=0,
                max_value=N_MODULES,
                value=(1, N_MODULES),
                step=1,
                key="data_range_2",
            )

        count_sweep_multi_pixel = create_count_sweep(
            df_transformed_list,
            count_type,
            data_range_2[0],
            data_range_2[1],
            x_values[axes_choice],
            include_summed_counts=include_summed_counts,
            *st.session_state.pixel_indices_sweep,
        )

        count_sweep_multi_pixel.update_layout(
            height=800, xaxis_title=f"{axes_choice} Stage Position (px)"
        )

        st.plotly_chart(count_sweep_multi_pixel)
