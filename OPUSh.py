#click buttons and enter information in webpage
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import time
from datetime import datetime
import os
import logging

#if file is older than 2 weeks, return file path
def get_file_age_in_weeks(file_path):
    #file_path = os.path.join(path, file)
    file_time = os.path.getmtime(file_path)
    file_age = datetime.now().timestamp() - file_time
    file_age_weeks = file_age/604800
    print(file_age_weeks)
    if file_age_weeks >= 0:
        print('File is older than 2 weeks')
        print(file_path)
        push_file(file_path)
        print('File has been pushed')
    else:
        print('File is younger than 2 weeks')
        print(file_path)
        print('File has not been pushed')

def push_file(file_path):
    driver = webdriver.Chrome('/usr/local/bin/chromedriver')
    action = ActionChains(driver)
    driver.get('https://geodesy.noaa.gov/OPUS/')
    time.sleep(8)
    #click "choose file" button with action chains
    driver.find_element(By.NAME, 'uploadfile').send_keys(file_path)

    #enter information in drop down menu
    elem = driver.find_element(By.ID, 'select2-ant_type-container').click()
    action.send_keys('JAVTRIUMPH_2A+P JVGR').perform()
    time.sleep(2)
    action.send_keys(Keys.ENTER).perform()
    time.sleep(1)
    #enter email address
    driver.find_element(By.NAME, 'email_address').send_keys('tviolette@usgs.gov')
    time.sleep(1)
    driver.find_element(By.NAME, 'Options').click()
    time.sleep(1)
    driver.find_element(By.NAME, 'SolutionFormat').click()
    action.send_keys(Keys.ARROW_DOWN).perform()
    time.sleep(1)
    action.send_keys(Keys.ARROW_DOWN).perform()
    time.sleep(1)
    action.send_keys(Keys.ENTER).perform()
    time.sleep(1)
    driver.find_element(By.NAME, 'Static').click()
    #if multiple alert boxes appears click OK in alert box
    try:
        alert = WebDriverWait(driver,5).until(EC.alert_is_present)
        alert = driver.switch_to.alert
        alert_text = alert.text
        logging.info(alert_text)
        alert.accept()
        logging.info('Alert accepted')
        print("alert accepted")
    except:
        print("no alert")
    try:
        alert = WebDriverWait(driver,5).until(EC.alert_is_present)
        alert = driver.switch_to.alert
        alert_text = alert.text
        logging.info(alert_text)
        alert.accept()
        logging.info('Alert accepted')
        print("alert accepted")
    except:
        print("no alert")
    try:
        alert = WebDriverWait(driver,5).until(EC.alert_is_present)
        alert = driver.switch_to.alert
        alert_text = alert.text
        logging.info(alert_text)
        alert.accept()
        logging.info('Alert accepted')
        print("alert accepted")
    except:
        print("no alert")
    
    #read text from next webpage
    time.sleep(5)
    text = driver.find_element(By.ID, 'container').text
    print(text)
#if text contains "upload successful" then remove extension from filename
    if 'Upload successful' in text:
        print('Upload successful')
        file = os.path.splitext(file_path)[0]
        ext = os.path.splitext(file_path)[1]
        os.rename(file_path, file + '_opus' + ext)
        logging.info('File has been renamed')
        print('File has been renamed')
    else:
        print('Upload unsuccessful')
        #store error to log file
        logging.error(text)
    driver.close()

