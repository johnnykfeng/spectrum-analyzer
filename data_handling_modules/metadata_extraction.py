import xml.etree.ElementTree as ET
from io import StringIO
import csv
import json
from extract_module import ExtractModule
from icecream import ic

def find_line_number(csv_file, target_string):
    line_numbers = []
    with open(csv_file, "r") as file:
        reader = csv.reader(file)
        for i, row in enumerate(reader):
            for cell in row:
                if target_string in cell:
                    line_number = i + 1
                    line_numbers.append(line_number)
                    # print(f"{target_string} found at line: {line_number}")
                    break
    # self.line_numbers = line_numbers
    return line_numbers

csv_file = r"data\module_voltage_data\Co57-30min-2000V_Cs137.csv"
# EM = ExtractModule(csv_file)
line_numbers = find_line_number(csv_file, "<meta>")
print(f"{line_numbers = }")
line_numbers = find_line_number(csv_file, "</meta>")
print(f"{line_numbers = }")

def get_metadata_lines(csv_file, start_tag = "<meta>", end_tag = "</meta>"):
    with open(csv_file, "r") as file:
        reader = csv.reader(file)
        metadata_lines = []
        # metadata_lines = ""
        start_found = False
        for row in reader:
            for cell in row:
                if start_tag in cell:
                    start_found = True
                    metadata_lines.append(row)
                    break
                if start_found:
                    metadata_lines.append(row)
                if end_tag in cell:
                    return metadata_lines
                
metadata_lines = get_metadata_lines(csv_file, start_tag="<DUT>", end_tag="</DUT>")
print(f"{metadata_lines = }")
metadata_string = "\n".join(["".join(row) for row in metadata_lines])
print(f"{metadata_string = }")
ic(metadata_string)

def convert_xml_to_json(xml_string):
    root = ET.fromstring(xml_string)
    metadata_dict = {}
    
    for child in root:
        if child.tag not in metadata_dict:
            metadata_dict[child.tag] = child.text
        
        # for sub_child in child:
        #     metadata_dict[child.tag][sub_child.tag] = sub_child.text
    
    json_data = json.dumps(metadata_dict)
    return json_data

metadata_json = convert_xml_to_json(metadata_string)
ic(metadata_json)

# Example metadata as a multiline string (you would replace this with reading from a file)
metadata_xml = """
<meta>
    <VersionInfo>
        <MetaVersionPurpose>H3D Metadata Template</MetaVersionPurpose>
        <MetaVersion>1.00</MetaVersion>
        <MetaVersionDate>2018-10-04</MetaVersionDate>
        <MetaVersionBlame>Helen Roy</MetaVersionBlame>
        <Copyright>Redlen Technologies</Copyright>
    </VersionInfo>
    <FileInfo>
        <Type></Type>
        <RecordLength></RecordLength>
        <DataFormat>csv</DataFormat>
        <DateCreated>Wednesday, April 24, 2024</DateCreated>
    </FileInfo>
    <DUT>
        <thickness>10</thickness>
        <pixelRows>11</pixelRows>
        <pixelCols>11</pixelCols>
    </DUT>
    <TestSettings>
        <Station>H3DTestBox003</Station>
        <SerialNumber>Am241-30min-2000V-NoMask</SerialNumber>
        <HVbias>2028</HVbias>
        <duration>00:30:01</duration>
        <startTemp>28.75</startTemp>
        <endTemp>28.00</endTemp>
    </TestSettings>
    <!-- Additional settings omitted for brevity -->
</meta>
"""

# Parsing the XML-like string
root = ET.parse(StringIO(metadata_xml)).getroot()
print(root)

# Function to extract metadata based on tag name
def extract_metadata_by_tag(root, tag):
    found = root.findall('.//{}'.format(tag))
    return [elem.text for elem in found]

# Example of extracting information
version_info = extract_metadata_by_tag(root, 'MetaVersion')
file_info = extract_metadata_by_tag(root, 'DataFormat')
dut_thickness = extract_metadata_by_tag(root, 'thickness')
test_settings_station = extract_metadata_by_tag(root, 'Station')

# Print extracted metadata
print("Version:", version_info)
print("File Format:", file_info)
print("DUT Thickness:", dut_thickness)
print("Test Station:", test_settings_station)

import xml.etree.ElementTree as ET

def convert_xml_to_json(xml_string):
    root = ET.fromstring(xml_string)
    metadata_dict = {}
    
    for child in root:
        if child.tag not in metadata_dict:
            metadata_dict[child.tag] = {}
        
        for sub_child in child:
            metadata_dict[child.tag][sub_child.tag] = sub_child.text
    
    json_data = json.dumps(metadata_dict)
    return json_data

# Example usage
json_metadata = convert_xml_to_json(metadata_xml)
ic(json_metadata)
