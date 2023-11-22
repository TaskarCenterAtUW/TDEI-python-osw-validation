# Get the folder for input file
import os
from python_osw_validation import OSWValidation

root_dir  = os.path.dirname(os.path.abspath(__file__))

files_dir = os.path.join(root_dir,'tests','unit_tests','test_files')
print(root_dir)
print(files_dir)
input_file = os.path.join(files_dir,'osw.zip')

## Validate the file
validator = OSWValidation(zipfile_path=input_file)
validation_result = validator.validate()
print(validation_result)
print(validation_result.is_valid)
print(len(validation_result.errors))
print(validation_result.errors)