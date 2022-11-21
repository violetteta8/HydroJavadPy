#click buttons and enter information in webpage
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import time
driver = webdriver.Chrome('/usr/local/bin/chromedriver')
action = ActionChains(driver)
driver.get('https://geodesy.noaa.gov/OPUS/')
main_page = driver.current_window_handle
time.sleep(8)
#click "choose file" button with action chains
driver.find_element(By.NAME, 'uploadfile').send_keys('C:\\Users\\tviolett\\Documents\\JavadCmdTestOPUS.22o')

#enter information in drop down menu
elem = driver.find_element(By.ID, 'select2-ant_type-container').click()
action.send_keys('JAVTRIUMPH_2A   NONE').perform()
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
#click OK in alert box
alert = driver.switch_to.alert
alert.accept()
time.sleep(1)
alert = driver.switch_to.alert
alert.accept()