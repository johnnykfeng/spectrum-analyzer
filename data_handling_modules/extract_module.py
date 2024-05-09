import os
import csv
from typing import List, Tuple
import pandas as pd
import numpy as np


class ExtractModule:
    """
    A class for extracting and transforming data from a CSV file.

    Parameters:
    - csv_file (str): The file path of the CSV file from H3D software.

    Methods:
    - count_lines(csv_file): Counts the number of lines in the CSV file.
    - find_line_number(csv_file, target_string): Finds the line numbers where the target string is found.
    - find_start_end_lines(target_string, extra_lines, module_number): Finds the start and end lines for extraction.
    - extract_module2df(module_number): Extracts the module data as a DataFrame.
    - transform_df(df, bin_peak, bin_width, n_bins): Transforms the DataFrame by adding new columns and calculating counts.
    """

    def __init__(self, csv_file):
        if csv_file.endswith(".xlsx"):
            print("You entered a .xlsx file")
            alternate_csv_file = csv_file.replace(".xlsx", ".csv")
            if not os.path.exists(
                alternate_csv_file
            ):  # check if the file has been converted
                print(f"Converting {csv_file} to {alternate_csv_file}...")
                self.csv_file = self.convert_xlsx_to_csv(csv_file)
            else:
                print(f"Found {alternate_csv_file}, load that instead.")
                self.csv_file = alternate_csv_file
        else:
            self.csv_file = csv_file

        # self.csv_file = csv_file # file path of the csv file from H3D software
        self.target_string = "H3D_Pixel"  # string to search for in the csv file
        self.number_of_pixels = (
            121  # determines number of rows to extract from csv file
        )
        self.n_pixels_x = 11  # number of pixels in x direction
        self.n_pixels_y = 11  # number of pixels in y direction
        self.total_line_count = self.count_lines()  # this is not used, but nice to have
        self.line_numbers = []
        self.start_line = None  # output of find_start_end_lines
        self.end_line = None  # output of find_start_end_lines
        self.extra_lines = 0
        self.dataframe = None  # output of extract_module2df
        self.all_df = []  # output of extract_all_modules2df
        self.all_df_new = []  # output of transform_all_df
        self.N_DF = 0  # number of DataFrames in the list

    @staticmethod
    def convert_xlsx_to_csv(input_xlsx_file):
        df = pd.read_excel(input_xlsx_file)
        output_csv_file = input_xlsx_file.replace(".xlsx", ".csv")
        df.to_csv(output_csv_file, index=False)
        return output_csv_file

    def count_lines(self):
        """
        Counts the number of lines in the CSV file.
        """
        try:
            with open(self.csv_file, "r") as file:
                return sum(1 for line in file)
        except:
            print("File not found")
            return None

    def find_line_number(self, csv_file, target_string):
        """
        Finds the line numbers where the target string is found in the CSV file.

        Parameters:
        - csv_file (str): The file path of the CSV file.
        - target_string (str): The string to search for.

        Returns:
        - list: The line numbers where the target string is found.
        """
        # line_numbers = []
        with open(csv_file, "r") as file:
            reader = csv.reader(file)
            for i, row in enumerate(reader):
                for cell in row:
                    if target_string in cell:
                        line_number = i + 1
                        self.line_numbers.append(line_number)
                        # print(f"{target_string} found at line: {line_number}")
                        break
        # self.line_numbers = line_numbers
        return self.line_numbers

    def find_start_end_lines(
        self, target_string: str, extra_lines=0, module_number=3
    ) -> Tuple[int, int]:
        """
        Finds the start and end lines for extraction.

        Parameters:
        - target_string (str): The string to search for in the CSV file.
        - extra_lines (int): The number of extra lines to include before and after the module data.
        - module_number (int): The module number (1-4) to extract.

        Returns:
        - tuple: The start and end lines for extraction.
        """
        if self.line_numbers == []:
            _ = self.find_line_number(self.csv_file, target_string)

        if type(module_number) != int:
            print("Module number must be an integer")
            return None

        self.extra_lines = extra_lines
        start_line = self.line_numbers[module_number - 1] - extra_lines
        # + 1 to include the header line
        end_line = start_line + self.number_of_pixels + extra_lines + 1
        self.start_line, self.end_line = start_line, end_line
        return start_line, end_line

    def extract_module2df(self, module_number=3) -> pd.DataFrame:
        """
        Extracts the module data from the CSV file as a DataFrame.

        Parameters:
        - module_number (int): The module number (1-4) to extract.

        Returns:
        - pandas.DataFrame: The extracted module data.
        """
        start_line, end_line = self.find_start_end_lines(
            self.target_string, module_number=module_number
        )
        start_lines_to_skip = np.arange(0, start_line - 1)
        n_rows = (end_line - start_line) - 1

        self.dataframe = pd.read_csv(
            self.csv_file,
            skiprows=start_lines_to_skip,
            nrows=n_rows,
            index_col=self.target_string,
            header=0,
        )
        return self.dataframe

    @property
    def number_of_bins(self):
        if self.dataframe is None:
            print("DataFrame is not loaded yet. Please run extract_module2df() first.")
            return None
        return len(self.dataframe.columns)

    def extract_all_modules2df(self) -> List[pd.DataFrame]:
        """
        Extracts all the module data from the CSV file as a DataFrame.

        Returns:
        - pandas.DataFrame: The extracted module data.
        """
        if self.line_numbers == []:
            self.find_line_number(self.csv_file, self.target_string)

        for i in range(len(self.line_numbers)):
            df_module = self.extract_module2df(
                module_number=i + 1
            )  # module_number is 1-based indexed
            self.all_df.append(df_module)
        self.N_DF = len(self.all_df)
        return self.all_df

    @property
    def number_of_modules(self):
        return len(self.all_df)

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
        if file_path.endswith(".xlsx"):
            print("You entered a .xlsx file")
            alternate_file_path = file_path.replace(".xlsx", ".csv")
            print(f"Converting {file_path} to {alternate_file_path}...")
            file_path = ExtractModule.convert_xlsx_to_csv(file_path)

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

        if file_path.endswith(".xlsx"):
            print("You entered a .xlsx file")
            alternate_file_path = file_path.replace(".xlsx", ".csv")
            print(f"Converting {file_path} to {alternate_file_path}...")
            file_path = ExtractModule.convert_xlsx_to_csv(file_path)

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


if __name__ == "__main__":
    csv_file = f"data\module_voltage_data\Cs137-30min-1000V_Cs137.csv"
    EM = ExtractModule(csv_file)
    # print(EM.number_of_columns)
    df = EM.extract_module2df(module_number=0)
    print(df.head())
    # number of columns in the DataFrame
    print(EM.number_of_bins)
