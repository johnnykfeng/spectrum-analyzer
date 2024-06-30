import plotly.express as px
import plotly.graph_objects as go
import numpy as np


def calculate_peak_count(array: np.array, peak_bin: int, peak_halfwidth=25):
    """Calculate the counts in a peak given the array and the peak bin number."""
    peak_count = np.sum(array[peak_bin - peak_halfwidth : peak_bin + peak_halfwidth])
    return peak_count


def add_peak_lines(fig, bin_peak, max_y, peak_halfwidth=25):
    fig.add_shape(
        type="line",
        x0=bin_peak,
        y0=0,
        x1=bin_peak,
        y1=max_y,
        line=dict(color="red", width=2),
        opacity=0.4,
    )
    fig.add_shape(
        type="line",
        x0=bin_peak - peak_halfwidth,
        y0=0,
        x1=bin_peak - peak_halfwidth,
        y1=max_y,
        line=dict(color="red", width=1, dash="dash"),
        opacity=0.5,
    )
    fig.add_shape(
        type="line",
        x0=bin_peak + peak_halfwidth,
        y0=0,
        x1=bin_peak + peak_halfwidth,
        y1=max_y,
        line=dict(color="red", width=1, dash="dash"),
        opacity=0.5,
    )

    return fig


def update_x_axis_range(fig, x_range):
    fig.update_xaxes(range=[min(x_range), max(x_range)])
    return fig


def update_y_axis_range(fig, y_range):
    fig.update_yaxes(range=[min(y_range), max(y_range)])
    return fig


def create_pixelized_heatmap(
    df,  # pd.DataFrame
    count_type: str,
    normalization="normalized",
    color_scale="Viridis",
    color_range: list[float] = None,
    text_auto=True,  # use ".3g" for 3 significant digits
):
    heatmap_table = df.pivot_table(
        index="y_index", columns="x_index", values=count_type
    )

    if normalization == "normalized" or normalization:
        max_pixel_value = heatmap_table.values.max()
        heatmap_table = (heatmap_table / max_pixel_value).round(2)

    if color_range is None:
        color_range = [heatmap_table.values.min(), heatmap_table.values.max()]

    heatmap_fig = px.imshow(
        heatmap_table,
        color_continuous_scale=color_scale,  # use color_scale variable for colorscale
        range_color=color_range,
        text_auto=text_auto,
        labels=dict(color="Value", x="X", y="Y"),
    )

    heatmap_fig.update_layout(
        xaxis=dict(title="X-index of Pixel"),
        yaxis=dict(title="Y-index of Pixel"),
        xaxis_nticks=12,
        yaxis_nticks=12,
        margin=dict(l=40, r=40, t=40, b=40),
        width=700,
        height=700,
    )

    return heatmap_fig


def create_spectrum_average(df, **kwargs):
    summed_array_bins = np.sum(df["array_bins"].values, axis=0)
    avg_array_bins = summed_array_bins / len(df)
    avg_total_counts = np.sum(df["total_count"].values) / len(df)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=np.arange(len(avg_array_bins)), y=avg_array_bins))

    if "bin_peak" in kwargs:
        avg_peak_counts = calculate_peak_count(avg_array_bins, kwargs["bin_peak"])
        if "peak_halfwidth" in kwargs:
            fig = add_peak_lines(
                fig, kwargs["bin_peak"], max(avg_array_bins), kwargs["peak_halfwidth"]
            )
        else:
            fig = add_peak_lines(fig, kwargs["bin_peak"], max(avg_array_bins))

    if "x_range" in kwargs:
        fig = update_x_axis_range(fig, kwargs["x_range"])

    if "y_range" in kwargs:
        fig = update_y_axis_range(fig, kwargs["y_range"])

    fig.update_layout(
        title=f"Average spectrum, Total count= {avg_total_counts:.1f}, Peak count= {avg_peak_counts:.1f} ",
        xaxis_title="Bin Index",
        yaxis_title="Average Counts",
        width=700,
        height=350,
    )

    return fig


def create_spectrum_pixel(
    df,
    *pixel_indices,
    **kwargs,
):
    fig = go.Figure()

    for pixel_index in pixel_indices:
        if isinstance(pixel_index, tuple):
            x_index, y_index = pixel_index
        else:
            raise ValueError("Pixel index must be a tuple of (x_index, y_index)")

        if (x_index is not None) and (y_index is not None):
            pixel_df = df[(df["x_index"] == x_index) & (df["y_index"] == y_index)]
            array_bins = pixel_df["array_bins"].values[0]
            fig.add_trace(
                go.Scatter(
                    x=np.arange(1, len(array_bins) + 1),
                    y=array_bins,
                    name=f"Pixel ({x_index}, {y_index})",
                )
            )
            if "bin_peak" in kwargs:
                if "peak_halfwidth" in kwargs:
                    fig = add_peak_lines(
                        fig,
                        kwargs["bin_peak"],
                        max(array_bins),
                        kwargs["peak_halfwidth"],
                    )
                else:
                    fig = add_peak_lines(fig, kwargs["bin_peak"], max(array_bins))

    if "x_range" in kwargs:
        fig = update_x_axis_range(fig, kwargs["x_range"])
    if "y_range" in kwargs:
        fig = update_y_axis_range(fig, kwargs["y_range"])

    fig.update_layout(
        xaxis_title="Bin #",
        yaxis_title="Counts",
        width=700,
        height=350,
    )

    # If only one pixel is selected, display the total and peak counts in the title
    if len(pixel_indices) == 1:
        total_count = pixel_df["total_count"].values[0]
        peak_count = pixel_df["peak_count"].values[0]
        fig.update_layout(
            title=f"Pixel ({x_index}, {y_index}), Total count = {total_count}, Peak count = {peak_count}",
        )

    return fig


def create_spectrum_pixel_sweep(
    df_list,
    x_index,
    y_index,
    min_data_range,
    max_data_range,
    colormap=px.colors.sequential.RdBu_r,
    **kwargs,
):
    total_num_modules = len(df_list)
    # print(f"Total number of modules: {total_num_modules}")
    df_list = df_list[min_data_range:max_data_range]
    fig = go.Figure()

    num_of_lines = len(df_list)

    labels = [f"{i}" for i in range(total_num_modules)]
    if "stage_x_mm" in kwargs:
        metadata = kwargs["stage_x_mm"]
        labels = metadata

    for i, df in enumerate(df_list):
        pixel_df = df[(df["x_index"] == x_index) & (df["y_index"] == y_index)]
        array_bins = pixel_df["array_bins"].values[0]
        color = colormap[int(i / num_of_lines * (len(colormap) - 1))]
        fig.add_trace(
            go.Scatter(
                x=np.arange(1, len(array_bins) + 1),
                y=array_bins,
                name=f"{labels[i+min_data_range]}",
                line_color=color,
            )
        )

    if "x_range" in kwargs:
        fig = update_x_axis_range(fig, kwargs["x_range"])
    if "y_range" in kwargs:
        fig = update_y_axis_range(fig, kwargs["y_range"])

    fig.update_layout(
        xaxis_title="Bin #",
        yaxis_title="Counts",
        # width=700,
        # height=650,
    )

    return fig


def create_count_sweep(
    df_list,
    count_type,
    min_data_range,
    max_data_range,
    x_values, 
    *pixel_indices,
    **kwargs,
):
    df_list = df_list[min_data_range:max_data_range]
    x_values = x_values[min_data_range:max_data_range]

    fig = go.Figure()
    
    for pixel_index in pixel_indices:
        if isinstance(pixel_index, tuple):
            x_index, y_index = pixel_index
        else:
            raise ValueError("Pixel index must be a tuple of (x_index, y_index)")

        counts = []
        for i, df in enumerate(df_list):
            pixel_df = df[(df["x_index"] == x_index) & (df["y_index"] == y_index)]
            count = pixel_df[count_type].values[0]
            counts.append(count)
        
        fig.add_trace(
            go.Scatter(
                x=x_values,
                y=counts,
                mode="lines",
                line=dict(
                    width=1.5,
                    #   dash="dash"
                ),
                name=f"Pixel ({x_index}, {y_index})",
            )
        )

        fig.add_trace(
            go.Scatter(
                x=x_values,
                y=counts,
                mode="markers",
                marker=dict(
                    size=8, color=x_values, colorscale="RdBu_r", showscale=False
                ),
                showlegend=True,
                name=f"Pixel ({x_index}, {y_index})",
            )
        )

    fig.update_layout(
        yaxis_title=f"{count_type}",
        showlegend=True,
        # width=700,
        # height=700,
    )
    fig.update_xaxes(
        showgrid=True,
        gridwidth=0.1,
        gridcolor="gray",
        #  minor_griddash="dot",
        griddash="dash",
    )

    return fig


# def create_count_sweep_old(
#     df_list,
#     x_index,
#     y_index,
#     count_type,
#     min_data_range,
#     max_data_range,
#     colormap=px.colors.sequential.RdBu_r,
#     *pixel_indices,
#     **kwargs,
# ):
#     total_num_modules = len(df_list)
#     df_list = df_list[min_data_range:max_data_range]
#     fig = go.Figure()

#     num_of_lines = len(df_list)

#     labels = [f"{i}" for i in range(total_num_modules)]
#     if "stage_x_mm" in kwargs:
#         metadata = kwargs["stage_x_mm"]
#         labels = metadata
#     print(f"{labels = }")

#     counts = []
#     for i, df in enumerate(df_list):
#         pixel_df = df[(df["x_index"] == x_index) & (df["y_index"] == y_index)]
#         count = pixel_df[count_type].values[0]
#         counts.append(count)
#         # color = colormap[int(i / num_of_lines * (len(colormap) - 1))]

#     x_values = labels[min_data_range:max_data_range]
#     fig.add_trace(
#         go.Scatter(
#             x=x_values,
#             y=counts,
#             mode="markers",
#             marker=dict(size=8, color=x_values, colorscale="RdBu_r", showscale=True),
#             # name=f"{x_values}",
#         )
#     )

#     fig.add_trace(  # white line to connect the markers
#         go.Scatter(
#             x=labels[min_data_range:max_data_range],
#             y=counts,
#             mode="lines",
#             line=dict(width=0.6),
#             line_color="white",
#             name="Counts trace",
#         )
#     )

#     # if 'x_range' in kwargs:
#     #     fig = update_x_axis_range(fig, kwargs['x_range'])
#     # if 'y_range' in kwargs:
#     #     fig = update_y_axis_range(fig, kwargs['y_range'])

#     fig.update_layout(
#         yaxis_title=f"{count_type}",
#         showlegend=False,
#         # width=700,
#         # height=850,
#     )
#     fig.update_xaxes(
#         showgrid=True,
#         gridwidth=0.1,
#         gridcolor="gray",
#         #  minor_griddash="dot",
#         griddash="dash",
#     )

#     return fig


def create_surface_plot_3d(figure, color_scale):
    # extract the data from the figure
    z_data = figure["data"][0]["z"]

    # create x and y coordinates
    x_data = list(range(len(z_data[0])))
    y_data = list(range(len(z_data)))

    # create 3D surface plot with the selected colorscale
    surface_plot_3d = go.Figure(
        data=[go.Surface(x=x_data, y=y_data, z=z_data, colorscale=color_scale)]
    )

    surface_plot_3d.update_layout(
        title="3D Surface Plot",
        autosize=False,
        width=700,
        height=700,
        margin=dict(l=65, r=50, b=65, t=90),
    )

    return surface_plot_3d
