import pandas as pd
import os

cwd = os.getcwd()
file_path = cwd + '/artifact/result/100_test_app_link.csv'

# Read the CSV file
df = pd.read_csv(file_path)

def check_inconsistency(row):
    delete_url = str(row.get('delete_account_url', '')).strip().lower()
    manage_url = str(row.get('manage_data_url', '')).strip().lower()
    deletion_info = str(row.get('Data Deletion Info', '')).strip().lower()

    # Check if a link is provided (not empty and not 'not found')
    has_link = any([
        delete_url and delete_url != 'not found',
        manage_url and manage_url != 'not found'
    ])
    
    # Inconsistency Case 1: Link is present but deletion info is 'cannot'
    if has_link and deletion_info == 'cannot':
        return 'inconsistency'
    
    # Inconsistency Case 2: No link but deletion info is 'can'
    if not has_link and deletion_info == 'can':
        return 'inconsistency'
    
    return 'consistency'

# Apply the function to each row
df['inconsistency'] = df.apply(check_inconsistency, axis=1)

# Save the updated DataFrame back to the CSV
df.to_csv(file_path, index=False)
