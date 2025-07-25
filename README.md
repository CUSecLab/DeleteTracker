# No Way to Sign Out? Unpacking Non-Compliance with Google Play’s App Account Deletion Requirements

Despite the significant convenience mobile apps bring to our daily lives, the collection and use of personal information by these apps remain a major concern, particularly regarding how such data is handled after users sign out. To align with regulations like the General Data Protection Regulation (GDPR) that have included specific provisions granting individuals the right to request data deletion, mobile app stores, such as Google Play, have introduced new account deletion requirements that require apps to provide proper account deletion methods. In this work, we conducted the first study on investigating non-compliance issues with Google Play’s app account deletion requirements. Starting with a pilot study of the top 50 apps on Google Play, we identified potential issues related to account deletion and defined three main categories of issues: link issues, content issues, and functionality issues. Based on these findings, we developed a tool named DELETETRACKER to automatically collect account deletion-related information from Google Play and semi-automatically identify non-compliance issues regarding account deletion. Using DELETETRACKER, we analyzed 863 Google Play apps’ account deletion information. Among the 494 apps with accessible account deletion links, DELETETRACKER discovered that only 8.5% of apps provide both in-app path and web-based account deletion methods, which fully comply with Google Play’s account deletion requirements. 64.6% of apps offer only one account deletion method. We also found 12 apps that failed to delete user accounts. We have reported our findings to Google through the vulnerability reporting process. Following our disclosure, Google acknowledged the reported issue and assigned it a Medium (S2) severity level.


# 📁 Project Structure

1. Account Deletion Link Crawler

    1.1 Mobile crawler: artifact/1_AccountDeletionLinkCrawler/1_mobile_crawler.py

    1.2 Web crawler: artifact/1_AccountDeletionLinkCrawler/2_web_crawler.py

2. Account Deletion Link Analyzer

    2.1 Cross-platform inconsistency: artifact/2_AccountDeletionLinkAnalyzer/inconsistency_check.py

    2.2 Inaccessible links: artifact/2_AccountDeletionLinkAnalyzer/Inaccessibility_check.py

    2.3 Same/similar links: artifact/2_AccountDeletionLinkAnalyzer/same_similar_link_check.py

3. Account Deletion Method Classifier

    3.1 Preprocessing

        3.1.1 Convert account deletion webpages to HTML: artifact/3_AccountDeletionMethodClassifier/web2html.py

        3.1.2 Convert HTML to plaintext: artifact/3_AccountDeletionMethodClassifier/HtmlToPlaintext-master

    3.2 Classification

        3.2.1 Detect missing account deletion method: artifact/3_AccountDeletionMethodClassifier/NLP_missing_deletion_info.py

        3.2.2 Detect in-app or web-based deletion methods (step-by-step): artifact/3_AccountDeletionMethodClassifier/NLP_stepbystep.py

        3.2.3 Detect web-based forms/buttons: artifact/3_AccountDeletionMethodClassifier/check_web_form_button.py

        3.2.4 Classify all deletion methods using ChatGPT: artifact/3_AccountDeletionMethodClassifier/GPT_classifier.py




# ⚙️ How to Run the Code

## 🔧 Prerequisites

1. Install Android Studio - https://developer.android.com/studio?gad_source=1&gad_campaignid=21831783525&gbraid=0AAAAAC-IOZnjGjGiJdj41SwNTctmqMcJy&gclid=CjwKCAjw6s7CBhACEiwAuHQckl9uhbNb3WxJdDBaXGxFhwVsfvcDfcYm388EOFnnuZxc7D6QOrFP5hoCtgwQAvD_BwE&gclsrc=aw.ds

2. Install node
    ```bash
    brew install node
    ```

3. Appium

    3.1 Install Appium - https://appium.io/docs/en/2.2/quickstart/install/

    3.1 Install the driver 
    ```bash
    appium driver install uiautomator2
    ```
    3.2 verify the installation
    ```bash
    appium driver list
    ```

4. Install Python dependencies
    ```bash
    pip install -r requirements.txt
    ```

5. Install spaCy language model

    ```bash
    python -m spacy download en_core_web_sm
    ```

6. Install Docker: https://www.docker.com/get-started/

7. ADB Setup and Emulator Verification: To run the mobile crawler or interact with Android emulators, you must ensure that `adb` (Android Debug Bridge) is installed and properly configured in your environment.

    7.1 If adb is not recognized in your terminal (zsh: command not found: adb), add the following lines to your ~/.zshrc:
    ```bash
    export ANDROID_HOME=$HOME/Library/Android/sdk
    export PATH=$ANDROID_HOME/emulator:$ANDROID_HOME/tools:$ANDROID_HOME/tools/bin:$ANDROID_HOME/platform-tools:$PATH
    ```

    7.2 Then reload the configuration
    
    ```bash
    source ~/.zshrc
    ```

    7.3 Verify ADB Connection
    
    ```bash
    adb devices
    ```

## ▶️ Execution

### Mobile Crawler (Please refer to example video.)

1. Open Android Studio.

2. Go to More Actions > Virtual Device Manager.

3. Create new device (Pixel 9 or Pixel 9 pro) and launch device.

4. Open Google Play in the virtual device.

    Ensure the emulator has:

    ✅ Google Play Store installed

    ✅ Chrome browser (install manually from Play Store if missing)

    ✅ Log in both Google Play Store and Chrome browser using your own Google account.

5. Verify the emulator is connected: adb devices

6. In a terminal, start Appium: appmium.

7. Run the mobile crawler: artifact/1_AccountDeletionLinkCrawler/1_mobile_crawler.py

### Account Deletion Method Classifier

1. First, run artifact/3_AccountDeletionMethodClassifier/web2html.py to get html files.

2. Lauch Docker.

3. Enter artifact/3_AccountDeletionMethodClassifier/HtmlToPlaintext-master folder and run ./build.sh and ./run.sh to transform html files to plaintext files. 

    3.1 Please refer to /artifact/3_AccountDeletionMethodClassifier/HtmlToPlaintext-master/README.md for more details if you have any questions. 

4. Please remember to exit artifact/3_AccountDeletionMethodClassifier/HtmlToPlaintext-master folder then execute the following scripts.

5. In the artifact/3_AccountDeletionMethodClassifier/GPT_classifier.py, replace API_key in Line 13 then execute the program.


6. All other scripts can be run directly (no specific execution order). Results will be saved automatically in the artifact/result directory. 


