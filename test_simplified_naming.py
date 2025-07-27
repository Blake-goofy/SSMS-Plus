"""Test the simplified naming logic"""
import os
import time

def test_naming_logic(temp_file, server, db, is_script_view_as):
    """Test the simplified naming logic"""
    
    # Extract the unique part from the original temp filename for both cases
    basename = os.path.basename(temp_file).replace('..sql', '.sql')
    if '_' in basename:
        unique_part = basename.split('_')[-1].replace('.sql', '')
    else:
        unique_part = basename.replace('.sql', '')
    
    if is_script_view_as:
        # Script View As workflow - use script prefix with original unique ID
        custom_filename = f"{server}_{db}_script_{unique_part}.sql"
        workflow = "Script View As"
    else:
        # Normal new query - use "new" prefix with original unique ID
        custom_filename = f"new_{server}_{db}_{unique_part}.sql"
        workflow = "Normal New Query"
    
    return custom_filename, workflow

# Test cases
test_cases = [
    ("C:\\temp\\abc123.sql", "AXIOM", "ILS", False),  # Normal new query
    ("C:\\temp\\xyz789.sql", "AXIOM", "DBA", True),   # Script View As
    ("C:\\temp\\AXIOM_ILS_def456.sql", "AXIOM", "ILS", False),  # Normal with prefix
    ("C:\\temp\\some_random_file.sql", "SERVER", "DATABASE", True),  # Script View As
]

print("Testing simplified naming logic:")
for temp_file, server, db, is_script_view_as in test_cases:
    filename, workflow = test_naming_logic(temp_file, server, db, is_script_view_as)
    print(f"Input: {os.path.basename(temp_file)} | Workflow: {workflow} | Output: {filename}")
