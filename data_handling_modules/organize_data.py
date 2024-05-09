import pandas as pd
import csv

class OrganizeData:
    """
    Input: df_transformed_list (list): A list of transformed DataFrames from the ExtractModule class.

    Output: all_data_dict (dict): A dictionary containing the following keys:
        - df (pandas.DataFrame): The original DataFrame.
        - heatmap_table (pandas.DataFrame): A pivot table for the heatmap.
        - edge_pixels_df (pandas.DataFrame): A DataFrame containing the edge pixels.
        - interior_pixels_df (pandas.DataFrame): A DataFrame containing the interior pixels.
        - max_total_counts (int): The maximum total counts.
        - sum_total_counts (int): The sum of total counts.
    """

    def __init__(self, df_transformed_list, csv_file, include_peak_count=False):
        self.df_transformed_list = df_transformed_list
        self.N_MODULES = len(df_transformed_list)
        self.csv_file = csv_file
        self.include_peak_count = include_peak_count
        self.x_positions = None
        self.y_positions = None
        self.all_data_dict = self.organize_all_data()
        self.df_plot = None

    def organize_all_data(self):
        """Main method to organize the data."""
        all_data_dict = {}

        for i, df in enumerate(self.df_transformed_list):
            heatmap_table = df.pivot_table(
                index="y_index", columns="x_index", values="total_count"
            )
            max_total_counts = df["total_count"].max()
            sum_total_counts = df["total_count"].sum()
            avg_total_counts = round(df["total_count"].mean(), 1)
            edge_pixels_df = df[df["is_edge"] == True]
            interior_pixels_df = df[df["is_edge"] == False]
            all_data_dict[i] = {
                "df": df,
                "heatmap_table": heatmap_table,
                "pixel_id_map": df.pivot_table(
                    index="y_index", columns="x_index", values="pixel_id"
                ),
                "edge_pixels_df": edge_pixels_df,
                "interior_pixels_df": interior_pixels_df,
                "max_total_counts": max_total_counts,
                "sum_total_counts": sum_total_counts,
                "avg_total_counts": avg_total_counts,
            }
            if self.include_peak_count:
                heatmap_peak_table = df.pivot_table(
                    index="y_index", columns="x_index", values="peak_count"
                )
                heatmap_non_peak_table = df.pivot_table(
                    index="y_index", columns="x_index", values="non_peak_count"
                )
                all_data_dict[i]["heatmap_peak"] = heatmap_peak_table
                all_data_dict[i]["heatmap_non_peak"] = heatmap_non_peak_table
                all_data_dict[i]["avg_peak_counts"] = round(df["peak_count"].mean(), 1)
                all_data_dict[i]["avg_non_peak_counts"] = round(df["non_peak_count"].mean(), 1)
            
        return all_data_dict

    def organize_line_plots(self):
        """
        Organizes the data for the line plots.
        Skips the first two x and y positions since they are background measurements.
        """
        self.x_positions = self.extract_metadata_list(
            self.csv_file, "Stage position x (in mm):"
        )
        x_positions = self.x_positions[2:]  # skip the first two
        self.y_positions = self.extract_metadata_list(
            self.csv_file, "Stage position y (in mm):"
        )
        y_positions = self.y_positions[2:]  # skip the first two

        df_plot_rows = []
        counter = 0
        for x_idx in range(1, 12):
            for y_idx in range(1, 12):
                counter += 1
                pixel_total_counts_list = []
                pixel_peak_counts_list = []
                pixel_non_peak_counts_list = []
                for i in range(2, self.N_MODULES):
                    df = self.all_data_dict[i]["df"]
                    pixel_df = df[(df["x_index"] == x_idx) & (df["y_index"] == y_idx)]
                    pixel_total_counts = pixel_df["total_count"].values[0]
                    pixel_total_counts_list.append(pixel_total_counts)
                    
                    if self.include_peak_count:
                        peak_count = pixel_df["peak_count"].max()
                        non_peak_count = pixel_df["non_peak_count"].max()
                        pixel_peak_counts_list.append(peak_count)
                        pixel_non_peak_counts_list.append(non_peak_count)
                        

                df_plot_rows.append(
                    {
                        "H3D_pixel": counter,  # 1 to 121
                        "x_index": x_idx,  # x_idx is an integer 1 to 11
                        "y_index": y_idx,  # y_idx is an integer 1 to 11
                        "x_position": x_positions,  # x_positions is a list
                        "y_position": y_positions,  # y_positions is a list
                        "total_counts": pixel_total_counts_list,  # also a list
                    }
                )
                if self.include_peak_count:
                    df_plot_rows[-1]["peak_counts"] = pixel_peak_counts_list
                    df_plot_rows[-1]["non_peak_counts"] = pixel_non_peak_counts_list
                    
                    
        self.df_plot = pd.DataFrame(df_plot_rows)
        return self.df_plot
    
    @staticmethod
    def extract_metadata(file_path, search_pattern, occurrence):
        """
        Input:
        - file_path (str): The file path of the CSV file.
        - search_pattern (str): The string to search for in the CSV file.
        - occurrence (int): The desired occurrence of the search pattern.
        Output:
        - str: The value found in the cell to the right of the search pattern.

        Extracts specific metadata from a CSV file.
        1. Open the CSV file and iterate through each row and cell.
        2. Search for the target string in each cell.
        3. If the target string is found, get the value in the cell to the right.
        4. Return the value if the desired occurrence is found.
        """
        with open(file_path, "r") as csvfile:
            reader = csv.reader(csvfile)
            occurrences_found = 0
            for row in reader:
                for cell in range(3):
                    # check if the stage coordinates string is in the cell
                    if search_pattern in row[cell]:
                        occurrences_found += 1
                        if (
                            occurrences_found == occurrence + 1
                        ):  # need +1 to get the correct occurrence
                            # get the number value in the cell to the right of the string
                            if cell < len(row) - 1:
                                return row[cell + 1]
                            else:
                                return None  # return none if there is no value to the right
        return None  # return None if occurrence is not found

    @staticmethod
    def extract_metadata_list(file_path, search_pattern):
        """
        Input:
        - file_path (str): The file path of the CSV file.
        - search_pattern (str): The string to search for in the CSV file.
        Output:
        - list: A list of values found in the cells to the right of the search pattern.

        Extracts specific metadata from a CSV file.
        1. Open the CSV file and iterate through each row and cell.
        2. Search for the target string in each cell.
        3. If the target string is found, get the value in the cell to the right.
        4. Append the value to a list.
        5. Return the list of values.
        """
        with open(file_path, "r") as csvfile:
            reader = csv.reader(csvfile)
            # create an empty list to store the values
            values = []
            for row in reader:
                for cell in range(3):
                    # check if the stage coordinates string is in the cell
                    if search_pattern in row[cell]:
                        # get the number value in the cell to the right of the string
                        if cell < len(row) - 1:
                            values.append(row[cell + 1])
                        else:
                            values.append(
                                None
                            )  # append none if there is no value to the right
        return values  # return the list of values