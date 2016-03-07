from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import traceback
import time
import shutil

CS2370_FOLDER = "CS2370_"
CS2370_BLACKBOARD_NAME = "20161_CS_2370_01_1: Intro to Computer Science III"

CS3240_FOLDER = "CS3240_"
CS3240_BLACKBOARD_NAME = "20161_CS_3240_01_1: Data Structures and Algorithms"

CS3560_FOLDER = "CS3560_"
CS3560_BLACKBOARD_NAME = "20161_CS_3560_01_1: Intro Systems Programming"

CLASS_NAME_FOLDER = CS3560_FOLDER
BLACKBOARD_CLASS_NAME = CS3560_BLACKBOARD_NAME
DOWNLOADED_FILE_DIR = os.path.join(os.getcwd(), "downloadedfiles")
USERNAME = "0"
PASSWORD = "0"


def condition_download_started(driver):
    """
    Return true if current working directory contains any file. Otherwise, continue polling
    """
    while True:
        flag = False
        for f in os.listdir(DOWNLOADED_FILE_DIR):
            if os.path.isfile(os.path.join(DOWNLOADED_FILE_DIR, f)):
                print("Started download")
                return True


def condition_download_finished(driver):
    """
    Return true if current working directory does not contain a file ending in ".part". Otherwise, continue polling
    """
    while True:
        flag = True
        for f in os.listdir(DOWNLOADED_FILE_DIR):
            if os.path.isfile(os.path.join(DOWNLOADED_FILE_DIR, f)) and f[-5:] == '.part':
                flag = False
        if flag is True:
            print("Completed download")
            return True


def create_and_move_all_to_folder(foldername):
    """
    Create a new folder named foldername, and move all files from the downloaded folder path into the new folder
    """
    foldername += "0"
    class_name_path = os.path.join(os.getcwd(), CLASS_NAME_FOLDER)
    dir_path = os.path.join(os.getcwd(), class_name_path, foldername)
    if not os.path.exists(class_name_path):
        os.makedirs(os.path.join(class_name_path))
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    else:
        foldername += str(int(foldername[-1]) + 1)
        dir_path = os.path.join(os.getcwd(), class_name_path, foldername)
        os.makedirs(dir_path)
    for f in os.listdir(DOWNLOADED_FILE_DIR):
        if os.path.isfile(os.path.join(DOWNLOADED_FILE_DIR, f)):
            current_path = os.path.join(DOWNLOADED_FILE_DIR, f)
            new_path = os.path.join(os.getcwd(), CLASS_NAME_FOLDER, foldername, f)
            shutil.move(current_path, new_path)
    print("Moved", foldername)


def main():
    if not os.path.isdir(DOWNLOADED_FILE_DIR):
        os.makedirs(DOWNLOADED_FILE_DIR)

    profile = webdriver.FirefoxProfile()
    profile.set_preference('browser.download.folderList', 2)
    profile.set_preference('browser.download.manager.showWhenStarting', False)
    profile.set_preference('browser.download.dir', DOWNLOADED_FILE_DIR)
    profile.set_preference('browser.helperApps.neverAsk.saveToDisk',
                           "text/x-c++hdr, application/octet-stream, image/png, text/plain")
    driver = webdriver.Firefox(profile)

    driver.get("https://bb.csueastbay.edu/webapps/login/?action=relogin")

    inputElement = driver.find_element_by_name("user_id")
    inputElement.send_keys(USERNAME)

    inputElement = driver.find_element_by_name("password")
    inputElement.send_keys(PASSWORD)

    inputElement.submit()
    try:
        element = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.LINK_TEXT, BLACKBOARD_CLASS_NAME)))
        element.click()

        element = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.LINK_TEXT, "Grade Center")))
        element.click()

        element = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.LINK_TEXT, "Needs Grading")))
        element.click()

        #element = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID,
        #"listContainer_nextpage_top")))
        #element.click()

        list_container = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.ID, "listContainer_databody")))

        table_length = len(list_container.find_elements_by_tag_name("tr"))
        for i in range(table_length):

            # list_container must be reassigned because the cache is emptied after navigating to a different page
            WebDriverWait(driver, 15).until(EC.title_contains("Needs Grading"))

            list_container = WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located((By.ID, "listContainer_databody")))
            tr = list_container.find_elements_by_tag_name("tr")

            # Column[2] = User Name, link, and possible attempt number
            # Column[3] = Date submitted and possible late assignment
            columns = tr[i].find_elements_by_css_selector("td, th")

            # ------------TODO ----------
            # also skip if Attempt(x of x) and x is not equal to x

            if "LATE" in columns[3].text:
                print("Skipping", columns[3].text)
                continue
            current_student = columns[2].text
            print("Entering", columns[2].text)

            # Grab and run javascript function to navigate to assignment page
            student_link = columns[2].find_element_by_css_selector("a")
            javascript_function = student_link.get_attribute("onclick").replace("javascript:", "")
            driver.execute_script(javascript_function)
            WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, "currentAttempt_label")))

            for link in driver.find_elements(By.CLASS_NAME, "dwnldBtn"):
                link.click()
                # filename = driver.find_elements(By.CLASS_NAME("attachment genericFile selected")).text
                time.sleep(1)
                WebDriverWait(driver, 15).until(condition_download_started)
                time.sleep(3)
                WebDriverWait(driver, 15).until(condition_download_finished)

            create_and_move_all_to_folder(current_student)

            driver.execute_script("window.history.go(-1)")
    except Exception:
        traceback.print_exc()
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
