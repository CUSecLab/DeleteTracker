import csv
from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy
from appium.options.android import UiAutomator2Options
from time import sleep
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv
import time
import os
import random

# Set up UiAutomator2Options for Google Play
options = UiAutomator2Options()
options.platformName = 'Android'
options.deviceName = 'emulator-5554'
options.platformVersion = '15.0'
options.appPackage = 'com.android.vending'
options.appActivity = 'com.google.android.finsky.activities.MainActivity'
options.automationName = 'UiAutomator2'
options.sessionOverride = True  

# Connect to the Appium server and launch Google Play
driver = webdriver.Remote('http://localhost:4723', options=options)
# os.system("adb shell pm clear com.android.vending")

# current working directory
cwd = os.getcwd()

input_file_path = cwd + '/artifact/result/10_test_app.csv'
output_file_path = cwd + '/artifact/result/10_test_app_link.csv'

# Initialize the output CSV file with headers if it doesn't exist
if not os.path.exists(output_file_path):
    # Create the output file and write the header row
    with open(output_file_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['pkg_name', 'app_name', 'delete_account_url', 'manage_data_url'])

# Click on the search box to start a new search
def click_search_box(pkg_name, app_name):
    found_app = False
    search_box = WebDriverWait(driver, 2).until(
        EC.presence_of_element_located((AppiumBy.XPATH, '//android.widget.TextView[@text="Search"]'))
    )
    search_box.click()
    
    search_input = driver.find_element(AppiumBy.XPATH, '//android.widget.TextView[@text="Search apps & games"]')
    search_input.click()

    input_txt = driver.find_element(AppiumBy.XPATH, '//android.widget.EditText')
    input_txt.send_keys(pkg_name)
    # Simulate pressing the "Enter" key on the keyboard to search
    driver.press_keycode(66)

    # Wait for search results to load
    # time.sleep(random.uniform(3, 10))
    sleep(1)
    # Click on the first app in the search results
    try:
    # Try to locate the app by its name
        first_result = WebDriverWait(driver, 0.5).until(
            EC.presence_of_element_located((AppiumBy.XPATH, f'//android.view.View[contains(@content-desc, "{app_name}")]'))
        )
        first_result.click()  # Click the app if found
        found_app = True
    except Exception as e:
        print(f"App '{app_name}' not found or doesn't match exactly. Skipping this app.")
        found_app = False
        with open(output_file_path, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([pkg_name, app_name, 'Skipping this app', 'Skipping this app'])
    
    return found_app

def find_delete_flag(pkg_name, app_name):
    for _ in range(4):
        found_delete = False
        manual_check = False
        try:
            delete_flag_button = WebDriverWait(driver, 1).until(
                EC.presence_of_element_located((AppiumBy.XPATH, '//android.widget.TextView[@text="You can request to delete collected data"]'))
            )
            found_delete = True
            delete_flag_button.click()
            break
        except:
            try:
                # //android.widget.TextView[@text="App doesn't provide a way to request data deletion"]
                no_provide = WebDriverWait(driver, 1).until(
                    EC.presence_of_element_located((AppiumBy.XPATH, '//android.widget.TextView[@text="App doesn\'t provide a way to request data deletion"]'))
                )
                found_delete = False
                break
            except:
                manual_check = True
                
            driver.find_element(
                AppiumBy.ANDROID_UIAUTOMATOR,
                'new UiScrollable(new UiSelector().scrollable(true)).scrollForward()'
            )
    if found_delete:
        sleep(1)
        find_url(pkg_name, app_name)
    if not found_delete and not manual_check:
        print(f"No delete flag found")
        with open(output_file_path, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([pkg_name, app_name, 'Not found', 'Not found'])
    if not found_delete and manual_check:
        print(f"Manual check required")
        with open(output_file_path, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([pkg_name, app_name, 'Manual', 'Manual'])
    
def find_url(pkg_name, app_name):
    delete_account_url = None
    manage_data_url = None

    # "Delete app account"
    try:
        delete_account_button = WebDriverWait(driver, 0.5).until(
            EC.presence_of_element_located((AppiumBy.XPATH, '//android.widget.TextView[@text="Delete app account"]'))
        )
        delete_account_button.click()
        sleep(1)

        try:
            url_field = WebDriverWait(driver, 1).until(
                EC.presence_of_element_located((AppiumBy.XPATH, '//android.widget.EditText[@resource-id="com.android.chrome:id/url_bar"]'))
            )
            delete_account_url = url_field.text
            print(f"Delete account URL: {delete_account_url}")
        except Exception as e:
            print(f"Exception occurred while retrieving 'Delete app account' URL: {e}")

        driver.back()  # return to the previous page

    except Exception:
        print(f"'Delete app account' button not found. Skipping.")

    # "Manage app data"
    try:
        manage_data_button = WebDriverWait(driver, 0.5).until(
            EC.presence_of_element_located((AppiumBy.XPATH, '//android.widget.TextView[@text="Manage app data"]'))
        )
        manage_data_button.click()
        sleep(1)

        try:
            url_field = WebDriverWait(driver, 1).until(
                EC.presence_of_element_located((AppiumBy.XPATH, '//android.widget.EditText[@resource-id="com.android.chrome:id/url_bar"]'))
            )
            manage_data_url = url_field.text
            print(f"Manage data URL: {manage_data_url}")
        except Exception as e:
            print(f"Exception occurred while retrieving 'Manage app data' URL: {e}")

        driver.back()  # return to the previous page

    except Exception:
        print(f"'Manage app data' button not found. Skipping.")
    
    driver.back()
    # save the URLs to the CSV file
    with open(output_file_path, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([pkg_name, app_name, delete_account_url, manage_data_url])

MAX_APP_RETRIES = 3  # each app can fail up to 3 times before skipping

def process_app(pkg_name, app_name):
    """ Process a single app by searching for it and finding the delete flag."""
    attempt = 0
    while attempt < MAX_APP_RETRIES:
        try:
            found_app = click_search_box(pkg_name, app_name)

            if not found_app:
                print(f"App '{pkg_name}' not found. Skipping without retrying.")
                return False  # jump to the next app if not found
            
            find_delete_flag(pkg_name, app_name)
            return True  # successfully processed the app

        except Exception as e:
            attempt += 1
            print(f"Error occurred while processing '{pkg_name}', attempt {attempt}: {e}")

            if attempt < MAX_APP_RETRIES:
                
                os.system("adb shell am start -n com.android.vending/com.google.android.finsky.activities.MainActivity")

                print(f"Retrying '{pkg_name}' due to unexpected error...")
                sleep(1)  
            else:
                print(f"Skipping '{pkg_name}' after {MAX_APP_RETRIES} failed attempts.")
                with open(output_file_path, mode='a', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow([pkg_name, app_name, 'Failed', 'Failed'])
                return False  

def main():
    existing_apps = set()
    with open(output_file_path, 'r', newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        for row in reader:
            if not row:
                continue
            existing_apps.add(row[0])

    with open(input_file_path, 'r', encoding='utf-8') as file:
        # read from second line to skip the header
        file.readline()
        reader = csv.reader(file)

        for row in reader:
            start_time = time.time()
            if len(row) < 2:
                print("Skipping row with insufficient data:", row)
                continue
            
            pkg_name = row[0]
            app_name = row[1]

            if pkg_name in existing_apps:
                print(f"App '{pkg_name}' already exists in the CSV. Skipping.")
                continue  # jump to the next app

            process_app(pkg_name, app_name)  # process the app, will skip after 3 failed attempts

            print(f"Time taken for {app_name}: {time.time() - start_time:.2f} seconds")
            sleep(1)
        

if __name__ == "__main__":
    
    os.system("adb shell am start -n com.android.vending/com.google.android.finsky.activities.MainActivity")
    main()
