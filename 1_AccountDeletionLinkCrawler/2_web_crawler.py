import pandas as pd
import requests
from bs4 import BeautifulSoup
import os

# current working directory
cwd = os.getcwd()
file_path = cwd + '/artifact/result/100_test_app_link.csv'
# read CSV file
df = pd.read_csv(file_path)  
df['Data Deletion Info'] = ''  # new column for results

count = 1

# iterate through the rows of the DataFrame
for index, row in df.iterrows():
    app_id = row['pkg_name']  
    print(count, ": ", app_id)
    url = f"https://play.google.com/store/apps/details?id={app_id}"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            page_text = soup.get_text()

            # check if the page text contains the required content
            if "You can request that data be deleted" in page_text:
                df.at[index, 'Data Deletion Info'] = 'can'
            else:
                df.at[index, 'Data Deletion Info'] = 'cannot'
        else:
            df.at[index, 'Data Deletion Info'] = 'Access Failed'
    except Exception as e:
        df.at[index, 'Data Deletion Info'] = 'Error'
    count += 1

# save the results to original CSV file
df.to_csv(file_path, index=False)
print("Finished")
