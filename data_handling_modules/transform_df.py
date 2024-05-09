import numpy as np
import pandas as pd
from typing import List


class TransformDf:
    def __init__(
        self,
        # extracted_df_list: List[pd.DataFrame],
        # bin_peak: int,
        # bin_width: int = 25,
        if_calculate_peak_count: bool = True,
    ):
        # self.extracted_df_list = extracted_df_list
        self.df_transformed_list = []
        self.N_DF = None
        # self.bin_peak = bin_peak
        # self.bin_width = bin_width
        self.if_calculate_peak_count = if_calculate_peak_count

    @staticmethod
    def calculate_peak_count(array: np.array, peak_bin: int, peak_halfwidth=25):
        """Calculate the counts in a peak given the array and the peak bin number."""
        peak_count = np.sum(
            array[peak_bin - peak_halfwidth : peak_bin + peak_halfwidth]
        )
        return peak_count

    @staticmethod
    def avg_neighbor_counts(df, x_index, y_index, count_type='peak_count'):
        sum_counts = 0
        neighbor_coords = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        neighbor_counter = 0
        for dx, dy in neighbor_coords:
            nx, ny = x_index + dx, y_index + dy
            if (nx in df['x_index'].values) and (ny in df['y_index'].values):
                neighbor_counter += 1
                sum_counts += df.loc[(df['x_index']==nx) & (df['y_index']==ny), count_type].values[0]
        avg_counts = sum_counts / neighbor_counter
        return avg_counts
    
    @staticmethod
    def leaking_ratio(row, count_type='peak_count'):
        return row['peak_count'] / row['avg_neighbor_counts']

    def transform_df(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Transforms a DataFrame by adding new columns and performing calculations.

        Args:
            df (pandas.DataFrame): The input DataFrame.
            bin_peak (int): The peak bin index, used to calculate the peak counts.
            bin_width (int, optional): The width of the bin range. Defaults to 25.
            n_bins (int, optional): The number of bin columns in the DataFrame. Defaults to 2000.

        Returns:
            pandas.DataFrame: The transformed DataFrame with additional columns.

        """
        
        df_bins = df.iloc[:, :] # grab all columns and rows from input DataFrame
        print(f"Number of bins (columns) in DataFrame: {df_bins.shape[1]}")
        # if df_bins.shape[1] != 200 and df_bins.shape[1] != 2000:
        #     print(f"{df_bins.shape[1] = }")
        #     raise ValueError("The DataFrame does not have the correct number of bins.")
        # elif df_bins.shape[0] != 121:
        #     raise ValueError("The DataFrame does not have the correct number of pixels.")
        
        df_new = pd.DataFrame(index=range(1, 122)) # create a new DataFrame with 121 rows
        if df_new.shape[0] != 121:
            raise ValueError("The DataFrame does not have the correct number of pixels.")

        df_new["x_index"] = np.nan
        df_new["y_index"] = np.nan

        for xi in range(11):
            for yi in range(11):
                df_new.loc[xi * 11 + yi + 1, "x_index"] = xi + 1
                df_new.loc[xi * 11 + yi + 1, "y_index"] = yi + 1

        # change data type to save memory
        df_new["x_index"] = df_new["x_index"].astype(int)
        df_new["y_index"] = df_new["y_index"].astype(int)
        df_new["pixel_id"] = df_new.index

        df_new["array_bins"] = df_bins.apply(lambda row: np.array(row), axis=1)

        df_new["total_count"] = df_new["array_bins"].apply(sum)
        df_new["total_count"] = df_new["total_count"].astype(int)
        df_new["total_counts_norm"] = round(
            df_new["total_count"] / df_new["total_count"].max(), 3
        )
        df_new["is_edge"] = (
            (df_new["x_index"] == 1)
            | (df_new["x_index"] == 11)
            | (df_new["y_index"] == 1)
            | (df_new["y_index"] == 11)
        )

        return df_new

    def add_peak_counts(self, df_new: pd.DataFrame, bin_peak, bin_width) -> pd.DataFrame:
        """Add the peak_count and non_peak_count columns to the DataFrame."""
        df_new["peak_count"] = df_new["array_bins"].apply(
            lambda x: self.calculate_peak_count(x, bin_peak, bin_width)
        )
        df_new["non_peak_count"] = df_new["total_count"] - df_new["peak_count"]
        
        return df_new  

    def transform_all_df(self, extracted_df_list: List[pd.DataFrame]):
        """
        Transforms all the DataFrames in the list.

        Args:
            n_bins (int, optional): The number of bin columns in the DataFrame. Defaults to 2000.

        Returns:
        - list: The transformed DataFrames with additional columns.
        """
        if extracted_df_list == []:
            raise ValueError("The input list is empty.")

        self.df_transformed_list = []  # reset the list
        for df in extracted_df_list:
            df_new = self.transform_df(df)
            self.df_transformed_list.append(df_new)
        self.N_DF = len(self.df_transformed_list)
        return self.df_transformed_list
    
    def add_peak_counts_all(self, bin_peak, bin_width):
        """Add the peak counts to all the DataFrames in the list."""
        for df_new in self.df_transformed_list:
            df_new = self.add_peak_counts(df_new, bin_peak, bin_width)
        return self.df_transformed_list