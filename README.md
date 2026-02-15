
# Payroll Data Test
This is an automated python script that performs 8 unit tests. 
The project folder has the following structure:
  - `test_payslip_data.py`
  - `\tests`
    - `\valid_data`
    - `\unit_test1`
    - `\unit_test2`
    ...
    - `\unit_test8`
  - `requirements.txt`
  - `README.md`

Each folder in `\tests` has 3 files in it:
  - `GTN.xlsx`
  - `Payrun.xlsx`
  - `mapping.json`

The only exception is `\unit_test1`, which contains `.csv` files for test purposes:
  - `GTN.csv`
  - `Payrun.csv`
  - `mapping.json`

Each `\unit_test` folder has it's files modified for the specific unit test to fail.
Only the `\valid_data` folder contains the original files. They will pass every unit test.

## Dependencies
The project dependencies are in the `requirements.txt` file. Everything runs on `Python`, using `pandas` and `pytest`.
To install the requirements for the script:
```
pip install -r requirements.txt
```

## How to Run the Project
Open a terminal, navigate to the project folder and type:

```
pytest
```

All 8 unit tests will run and you'll see which checks pass or fail with error details.

## Unit Tests
1. The File is of type excel 
2. The GTN file contains line breaks i.e. empty lines
3. The GTN file header structure has changed e.g. there are two header rows instead of one 
4. Employees are Present in the Payrun File but missing in the GTN file. 
5. Employees are Present in the GTN but missing in the Payrun File. 
6. Pay Elements in the GTN file do not have a mapping in the Payrun File. 
7. Pay Elements in the Payrun file do not have a mapping in the GTN File. 
8. For Pay Elements in the GTN file, the values have a numeric type. 

## File Modifications
The files in each unit folder are modified as such:
 - `unit_test1`: 
 	- `GTN.xlsx` -> `GTN.csv`
 	- `Payrun.xlsx` -> `Payrun.csv`
   Note: Created a simple script to convert `.xlsx` => `.csv` but it is not in the project. 
         It is a simple pandas operation of reading an excel extension file and saving it as `.csv` file.
 - `unit_test2`:
 	- `GTN.xlsx` -> inserted 2 empty rows in the records
 - `unit_test3`: 
 	- `GTN.xlsx` -> inserted an additional header above the old header
 - `unit_test4`:
 	- `GTN.xlsx` -> removed employees - `1004`, `1014`, `1024`, `1034`
 - `unit_test5`:
 	- `Payrun.xlsx` -> removed employees - `1004`, `1014`, `1024`, `1034`
 - `unit_test6`:
 	- `Payrun.xlsx`
    	changed column: `Bonus` -> `Bonus1`
    	changed column: `Backpay` -> `Backpay1`
 - `unit_test7`:
	- `GTN.xlsx`
    	changed column: `element4` -> `element44`
    	changed column: `element9` -> `element99`
 - `unit_test8`:
 	- `GTN.xlsx`
    	changed cell value where employee_id=1000 and column=element4
		new value is non-numerical => "Hello World"




