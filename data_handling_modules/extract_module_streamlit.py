import os
import csv
from typing import List, Tuple
import pandas as pd
import numpy as np
import codecs


class ExtractModuleStreamlit:

    def __init__(self, csv_file=None):
        self.csv_file = csv_file  # file path of the csv file from H3D software
        self.target_string = "H3D_Pixel"  # string to search for in the csv file
        self.number_of_pixels = 121  # determines number of rows to extract from csv file
        self.n_pixels_x = 11  # number of pixels in x direction
        self.n_pixels_y = 11  # number of pixels in y direction
        self.line_numbers = []
        self.start_line = None  # output of find_start_end_lines
        self.end_line = None  # output of find_start_end_lines
        self.extra_lines = 0
        self.dataframe = None  # output of extract_module2df
        self.df_list = []  # output of extract_all_modules2df
        self.N_DF = 0  # number of DataFrames in the list

    @staticmethod
    def find_line_number(csv_file, target_string):
        text_io = codecs.getreader("utf-8")(csv_file)
        reader = csv.reader(text_io)
        line_numbers = []
        for row_index, row in enumerate(reader):
            for cell in row:
                if target_string in cell:
                    line_numbers.append(row_index)
        return line_numbers
    
    @property
    def number_of_bins(self):
        if self.dataframe is None:
            print("DataFrame is not loaded yet. Please run extract_module2df() first.")
            return None
        return len(self.dataframe.columns)

    def extract_all_modules2df(self) -> List[pd.DataFrame]:
        self.line_numbers = ExtractModuleStreamlit.find_line_number(
                self.csv_file, self.target_string)

        self.df_list = []  # reset the list
        for i in range(len(self.line_numbers)):
            print(f"Extracting module {i+1} of {len(self.line_numbers)}")
            self.csv_file.seek(0)
            df = pd.read_csv(self.csv_file,
                             skiprows=self.line_numbers[i],
                             nrows=self.number_of_pixels,
                             index_col=self.target_string,
                             header=0
                             )
            self.df_list.append(df)
        return self.df_list
            
    @property
    def number_of_modules(self):
        return len(self.df_list)

    @staticmethod
    def extract_metadata_list(csv_file, string_pattern):
        """Extract metadata values from the csv file.
        """
        text_io = codecs.getreader("utf-8")(csv_file)
        reader = csv.reader(text_io)
        values = [] 
        for row_index, row in enumerate(reader):
            for cell in range(3):
                # check if the search pattern is in the cell
                if string_pattern in row[cell]:
                    # get the number value in the next cell
                    if cell< len(row)-1:
                        values.append(row[cell+1])
                    else:
                        values.append(None)
        return values

