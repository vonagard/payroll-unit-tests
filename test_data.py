import json
import pandas as pd
import pytest
from pathlib import Path

UNIT_TEST_FOLDERS = [
    f"tests/{name}" for name in [
        "valid_data", "unit_test1", "unit_test2", "unit_test3", "unit_test4",
        "unit_test5", "unit_test6", "unit_test7", "unit_test8"
    ]
]

def find_file(folder, name):
    for file in Path(folder).iterdir():
        if file.is_file() and file.stem.lower() == name:
            return file
    return None


def is_excel_file(path):
    return getattr(path, "suffix", "").lower() in {".xlsx", ".xls", ".xlsm"}


def load_test_files(folder):
    folder_path = Path(folder)
    output_files = []

    try:
        file_path = folder_path / "GTN.xlsx"
        gtn_file = pd.read_excel(file_path)
        output_files.append(gtn_file) 
    except Exception as e:
        pytest.fail(f"Failed to loead GTN.xlsx in {folder}. Error: {e}")
    
    try:
        file_path = folder_path / "Payrun.xlsx"
        payrun_file = pd.read_excel(file_path, header=[0, 1])
        output_files.append(payrun_file)
    except Exception as e:
        pytest.fail(f"Failed to load Payrun.xlsx in {folder}. Error: {e}")

    try:
        file_path = folder_path / "mapping.json"
        with open(file_path, "r") as mapping_file:
            mapping_data = json.load(mapping_file)
        output_files.append(mapping_data)
    except Exception as e:
        pytest.fail(f"Failed to load mapping.json in {folder}. Error: {e}")


    return output_files  # Order of return: [GTN.xlsx, Payrun.xlsx, mapping.json]


# Employee ID key map -> GTN[0], Payrun[1]
employee_id_mapping = ["employee_id", "Employee ID"]


####  Unit Test 1: Check if GTN file is an Excel file  ####
@pytest.mark.parametrize("folder", UNIT_TEST_FOLDERS)
def test_gtn_is_excel(folder):
    for file in Path(folder).iterdir():
        if file.is_file() and file.stem.lower() == "gtn":
            assert file, f"No GTN file found in {folder}"
            assert is_excel_file(file), f"GTN file is not an Excel format: {file}"
####  Unit Test 1: Check if Payrun file is an Excel file  ####
@pytest.mark.parametrize("folder", UNIT_TEST_FOLDERS)
def test_payrun_is_excel(folder):
    for file in Path(folder).iterdir():
        if file.is_file() and file.stem.lower() == "payrun":
            assert file, f"No Payrun file found in {folder}"
            assert is_excel_file(file), f"Payrun file is not an Excel format: { file}"


####  Unit Test 2: Check for empty lines in GTN file  ####
@pytest.mark.parametrize("folder", UNIT_TEST_FOLDERS)
def test_empty_lines(folder):
    files = load_test_files(folder)
    gtn_df = files[0]
    assert not gtn_df.isnull().all(axis=1).any(), f"{folder} has empty rows in the GTN file"


####  Unit Test 3: Check if GTN file has a single header row  ####
@pytest.mark.parametrize("folder", UNIT_TEST_FOLDERS)
def test_has_single_header(folder):
    files = load_test_files(folder)
    gtn_df = files[0]

    if all(str(col).startswith('Unnamed') or str(col).strip() == '' for col in gtn_df.columns):
        raise AssertionError(f"{folder} GTN file appears to have no header row.")
    def is_header_like(row):
        return all(isinstance(val, str) or pd.isnull(val) for val in row)
    for i in range(min(3, gtn_df.shape[0])):
        row = gtn_df.iloc[i].values
        if is_header_like(row):
            raise AssertionError(f"{folder} GTN file has more than one header row.")


####  Unit Test 4 and 5  ####
# Unit Test 4: Employees present in Payrun file are missing from GTN file.
# Unit Test 5: Employees present in GTN file are missing from Payrun file.
@pytest.mark.parametrize("folder", UNIT_TEST_FOLDERS)
def test_employees_in_payrun(folder):
    files = load_test_files(folder)
    gtn_df = files[0]
    payrun_df = files[1]
    gtn_id_map, payrun_id_map = employee_id_mapping
    
    col_tuple_payrun = next((c for c in payrun_df.columns if isinstance(c, tuple) and c[0] == payrun_id_map), None)
    
    def normalize_id(id_value):
        if pd.isnull(id_value): 
            return None
        
        str_id_value = str(id_value).strip()

        if not str_id_value or str_id_value.lower() == 'nan': 
            return None
        
        return str_id_value[:-2] if str_id_value.endswith('.0') else str_id_value
    
    payrun_ids = set(filter(None, map(normalize_id, payrun_df[col_tuple_payrun].to_list()))) if col_tuple_payrun else set()
    gtn_ids = set(filter(None, map(normalize_id, gtn_df[gtn_id_map].to_list())))
    
    missing_emp_gtn = payrun_ids - gtn_ids
    assert not missing_emp_gtn, f"ID of missing employees in the GTN file: {', '.join(map(str, missing_emp_gtn))}"
    
    missing_emp_payrun = gtn_ids - payrun_ids
    assert not missing_emp_payrun, f"ID of missing employees in the Payrun file: {', '.join(map(str, missing_emp_payrun))}"


####  Unit Test 6 and 7  ####
# Unit Test 6: Pay Elements in the GTN file do not have a mapping in the Payrun File.
# Unit Test 7: Pay Elements in the Payrun file do not have a mapping in the GTN File.
@pytest.mark.parametrize("folder", UNIT_TEST_FOLDERS)
def test_pay_elements_mapping(folder):
    files = load_test_files(folder)
    gtn_df = files[0]
    payrun_df = files[1]
    mapping_json = files[2]

    mapping_dict = {k: v["vendor"] for k, v in mapping_json["mappings"].items() if v.get("map")}
    
    def normalize_element(element): return ''.join(str(element).lower().split())
    
    payrun_column_names = {
        normalize_element(x) for c in payrun_df.columns 
        for x in (c if isinstance(c, tuple) else (c,))}
    gtn_column_names = {
        normalize_element(col) for col in gtn_df.columns}
    
    missing_payrun = [element for element in mapping_dict if normalize_element(element) not in payrun_column_names]
    assert not missing_payrun, f"Missing mapped Payrun columns in headers: {missing_payrun}"

    missing_gtn = [element for element in mapping_dict.values() if normalize_element(element) not in gtn_column_names]
    assert not missing_gtn, f"Missing mapped GTN columns: {missing_gtn}"


#### Unit Test 8: Check if mapped pay element columns in GTN file are numeric ####
@pytest.mark.parametrize("folder", UNIT_TEST_FOLDERS)
def test_if_numeric(folder):
    files = load_test_files(folder)
    gtn_df = files[0]
    mapping_json = files[2]

    pay_elements = [mapping["vendor"] for mapping in mapping_json["mappings"].values() if mapping.get("map")]
    for element in pay_elements:
        if element not in gtn_df.columns:
            pytest.fail(f"Pay Element column '{element}' not found in GTN file.")
        non_numeric = gtn_df[element][~gtn_df[element].apply(lambda x: pd.isnull(x) or isinstance(x, (int, float)))]
        assert non_numeric.empty, f"The column '{element}' in GTN file contains non-numeric values: {non_numeric.tolist()}"
