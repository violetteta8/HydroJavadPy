import sys

sys.path.insert(0,'C:\\Users\\tviolett\\Documents\\GitLab\\HydroJavadPy\\')

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
import logging
import serial
import time
from datetime import datetime
import os

global path
from config import ComA, BaudA, ComB, BaudB, Site, SiteNumber, path
import sftp
from loggerConfig import configure_logger

count = 0
global t_end

def get_file_age_in_weeks(file_path):
    time.sleep(2)
    file_time = os.path.getmtime(file_path)                  # Get file creation time in seconds
    file_age = datetime.now().timestamp() - file_time        # Get file age in seconds
    file_age_weeks = file_age/604800                         # Convert file age to weeks
    if file_age_weeks >= 0.17:                                  #if older than 3 hours
        logging.info(file_path + ' is older than 2 weeks, attempting to push to OPUS')
        push_file(file_path)
        print('File has been pushed')
    else:
        logging.info(file_path + ' is younger than 2 weeks, file has not been pushed')
        print(file_path)

def push_file(file_path):
    try:
        # Open Chrome and go to OPUS website
        driver = webdriver.Chrome()                        #Open chrome browser
        action = ActionChains(driver)                      #Make action variable to use action chains
        driver.get('https://geodesy.noaa.gov/OPUS/')       #Open OPUS website
        wait = WebDriverWait(driver, 10)                   #Make Wait Variable to wait for page to load

        # Enter file path to upload
        wait.until(EC.presence_of_element_located((By.NAME, 'uploadfile'))).send_keys(file_path) #Wait for choose file button to appear
        #choose_file_button.send_keys(file_path)            #Enter file path to upload

        # Enter antenna type in drop down menu
        driver.find_element(By.ID, 'select2-ant_type-container').click() #Find antenna type drop down menu
        action.send_keys('JAVTRIUMPH_2A+P JVGR').perform()                         #Enter antenna type
        time.sleep(2)
        action.send_keys(Keys.ENTER).perform()                     #Click enter

        #Enter email address
        driver.find_element(By.NAME, 'email_address').send_keys('tviolette@usgs.gov') #Find email address boperform()
        time.sleep(1)
        #Click Options
        driver.find_element(By.NAME, 'Options').click() #find options button
        #action.click().perform()                          #click options button
        time.sleep(2)
        #Click Solution Format
        driver.find_element(By.NAME, 'SolutionFormat').click()              #Click solution format drop down menu
        action.send_keys(Keys.ARROW_DOWN).perform()                         #navigate to XML option
        action.send_keys(Keys.ARROW_DOWN).perform()
        action.send_keys(Keys.ENTER).perform()
        time.sleep
        #Click Static
        driver.find_element(By.NAME, 'Static').click()                       #find and click static button

        alertpresent = True
        while alertpresent == True:
            try:
                alert = WebDriverWait(driver,5).until(EC.alert_is_present()) #wait for alert box to appear
                alert = driver.switch_to.alert                               #switch to alert box
                alert_text = alert.text                                      #get alert text
                logging.info(alert_text)                                     #log alert text
                alert.accept()                                               #accept alert
                logging.info('Alert accepted')
                alertpresent = True                                          #set alertpresent to true
                if 'invalid' in alert_text or 'too many' in alert_text:     #if alert text contains invalid or too many, exit
                        logging.info(alert_text)                            #log alert text
                        return                                              #exit loop as these mean invalid file names
                continue                                                    #continue loop as these mean invalid file names
            except TimeoutException:
                logging.info('No alert box')
                alertpresent = False
                break

        wait.until(EC.presence_of_element_located((By.ID, 'container')))    #wait for final message to appear

        text = driver.find_element(By.ID, 'container').text                 #get final message
        
        if 'Upload successful' in text:                                     #check if upload was successful, if so, rename file
            logging.info(file_path + ' upload to OPUS successful.')
            file = os.path.splitext(file_path)[0]
            ext = os.path.splitext(file_path)[1]
            os.rename(file_path, file + '_opus' + ext)
            logging.info('File has been renamed to ' + file + '_opus' + ext)
        else:
            logging.info(file_path + ' upload to OPUS unsuccessful.')
    except Exception as e:                                                  #handle exceptions
        logging.info('Upload to OPUS failed.')
        logging.info(e)
    finally:                                                                #close brower if it's still open
        if driver:
            driver.close()

def ingestGNSS():
    global count
    time.sleep(2)
    bytesToRead = ser.inWaiting()                                           # Check buffer for bytes available
    print(bytesToRead)                                                      # Print how many bytes are in buffer
    rl = ser.read(bytesToRead)                                              # Read number of bytes in buffer to "rl"
    print(rl)                                                               # Print the bytes
    file.write(rl)
    count = count + 1
    if count > 30:
        count = 0
    return count

def checkUpdates():
    global shutdown
    global SampleDur
    global t_end
    bytesToRead2 = ser2.inWaiting()                                         # Check buffer for bytes available in Datalogger port
    if bytesToRead2 > 0:                                                    # If there are bytes in the datalogger port
        DLStr = ser2.read_until('\n', bytesToRead2)                         # Read the bytes into DLStr
        DLStr = DLStr.decode('utf-8')                                       # Decode the bytes into a string
        if 'Shutdown' in DLStr:                                             # If the string "Shutdown" is in the bytes read
            logging.info('Shutdown command received')                       # Log that the shutdown command was received
            ser2.flush()                                                    # Flush the datalogger port
            ser2.write(b'Shutdown Received\r')                               # Send "Shutdown" back to datalogger
            ser2.flush()                                                    # Flush the datalogger port
            shutdown = 'True'                                               # Set shutdown variable to True                                          # Set ShutdownStr to the string received from datalogger
        elif 'End Sample' in DLStr:                                         # If the string "End Sample" is in the bytes read
            logging.info('End Sample command received')                     # Log that the End Sample command was received
            ser2.flush()                                                    # Flush the datalogger port
            ser2.write(b'End Sample Received\r')                             # Send "End Sample" back to datalogger
            ser2.flush()                                                    # Flush the datalogger port
            t_end = time.time()                                             # Set end time to current time
        elif DLStr.startswith('SID'):
            splitdata = DLStr.split(",")
            print(splitdata)                                                    # Print value to know how many bytes are expected
            SIDholder = splitdata[0].split(":")
            print(SIDholder)
            SID = SIDholder[1]
            print(SID)
            StationNum = splitdata[1]
            print(StationNum)
            SampleDur = splitdata[2]
            print(SampleDur)
            SampleDur = int(SampleDur)
            SampleDur = SampleDur * 60
            t_end = t_end + SampleDur
            logging.info('New Sample Duration Received')
            ser2.flush()
            ser2.write(b'Sample Info Received\r')
            ser2.flush()
    else:
        ser2.flush()
        ser2.write(b'No Data\r')
        ser2.flush()

currentmonth = datetime.now().month
wateryear = sftp.CheckWY()

newpath = 1
msg = ''
sitedirname = SiteNumber + '_' + Site                                       #create variable to name a directory "12345678_SID"


configure_logger(path)                                                      #set up logger
logger = logging.getLogger()

try:                                                                        # Try to make the path by making new directory
    os.makedirs(path)
    newpath = -1
except OSError as error:                                                    # If path already exists
    print(error)                                                           # Print the error message
    msg = error
    newpath = 0

if newpath == -1:
    logging.info('New directory created.')
else:
    logging.info(msg)


timestr = time.strftime("%Y%m%d_%H%M")                                      #set timestring to format YYYYmmdd_HHMM
SampleDur = 0                                                               # Declare variable to hold user-defined sample duration
SampleGNSS = 1
TestStr = ""
splitdata = 0
SID = 0
SIDholder = 0
StationNum = 0
ShutdownStr = ''
shutdown = 'False'

#open serial port to data logger
try:
    ser2 = serial.Serial(ComB,BaudB)
    logging.info('Serial port B Opened')
except:
    logging.exception('Serial Port B Not Available')

ser2.flushInput()                                                           # Flush Serial Port 2 Inbound buffer to ensure no junk bytes are present
ser2.flushOutput()                                                          # Flush Serial Port 2 Outbound buffer to ensure no junk bytes are present
time.sleep(3)                                                               # Short delay to ensure buffer was flushed.


while SampleDur == 0 and (SampleGNSS != 0 or SampleGNSS != -1):             # If SampleDur is 0, no data has come in from datalogger so:
    bytesToRead = ser2.inWaiting()                                          # Check if there are any bytes in the port, assign to "bytesToRead"
    print(bytesToRead)                                                      # Print value in command window
    if bytesToRead == 0:                                                    # If there are no bytes to read:
        ser2.write(b'Ready\r')                                              # Send "Ready<CR><LF>" out to datalogger to notify the datalogger the PC is ready to run the script
        ser2.flushInput()                                                   # Flush both inboud and outbound buffers as the "Ready" message is now in the dataloggers serial buffer
        ser2.flushOutput()
        time.sleep(60)                                                      # Delay 1 minute before returning to top of While loop as that's the scan rate of datalogger
    else:
        TestStr = ser2.read_until('\n', bytesToRead)                        # If not 0 or > 3 bytes from "inWaiting()", read number of bytes into SampleDur
        print(TestStr)                                                      #SampleDur = int(SampleDur)
        TestStr = TestStr.decode("utf-8")
        if TestStr.startswith('SID'):
            splitdata = TestStr.split(",")                                  # Change variable from type Bytes to type Integer
            print(splitdata)                                                # Print value to know how many bytes are expected
            SIDholder = splitdata[0].split(":")
            print(SIDholder)
            SID = SIDholder[1]
            print(SID)
            StationNum = splitdata[1]
            print(StationNum)
            SampleDur = splitdata[2]
            print(SampleDur)
            SampleGNSS = -1
        elif TestStr == 'No Sample':
            SampleGNSS = 0
            break
        else:
            SampleDur == 0
        ser2.flushInput()                                                   # Flush both ports
        ser2.flushOutput()
        time.sleep(5)                                                       # Delay a few seconds before moving into sampling loop

if SampleGNSS == -1:

    SampleDur = int(SampleDur)

#only open serial port if we are going to sample
    try:
        ser = serial.Serial(ComA,BaudA)
        logging.info('Serial port A Opened')
    except:
        logging.exception('Serial Port A Not Available')

# Create timestamp string for file naming
    fn = SiteNumber + "_" + Site + "_"                                          # Define site ID for file naming -- Do this via communication to datalogger?
    ext = ".jps"                                                                # Set raw file name extension from Javad to .jps
    jpsname = fn + timestr + ext                                                # Concatenate to make file name
    t_end = time.time()+ SampleDur * 60                                         # Set end time "t_end" to current time + user define minutes * 60s
    file = open(os.path.join(path,jpsname),'wb')                                # Open a new file in directory for binary writing
    cmdA = """cmd /c "jps2rin.exe """                                           # Set command line commands to convert the .jps to RINEX file type for OPUS
    cmdB = " /opus /o="
    cmdC = " /of="
    cmdstr = cmdA + path + jpsname + cmdB + path + cmdC + fn + timestr + '"'    # Create full command line string

    ser.write(bytes(b'em,,/msg/def\r\n'))                                       # Send "enable default message output" command to Javad through Serial Port 1
    time.sleep(1)                                                               # Wait 1 second before moving into sample loop

    file.truncate(0)                                                            # Ensure file is completely clean before sample loop

    print('Run Started')                                                
    while time.time() < t_end and shutdown == 'False':                          # While current time is less than end time and shutdown is false:
        ingestGNSS()
        if count == 30:
            checkUpdates()

    file.close()                                                                # After While loop finishes
    ser.write(bytes(b'dm,,/msg/def\r\n'))                                       # Send "disable message output" command to Javad
    time.sleep(1)                                                               # Delay 1 second
    ser.close()                                                                 # Close both serial port A
    os.system(cmdstr)                                                           # Output the command-line command to convert .jps to RINEX

numfiles = len([name for name in os.listdir(path) if name.endswith('o') if '_sftp' not in name]) # Check directory for files ending in "o" (indicating OPUS file), store the count in "numfiles"
print(numfiles)
numFiles = str(numfiles)
logging.info(numFiles + ' files to push to FTP.')                            # Print the number of OPUS files
if numfiles >= 1:                                                            # If more than X -- perhaps always send after every sample period instead of waiting for multiple files? Unless user starts manually?
    sftp.sftpConnect(path)
        

for file in os.listdir(path):
    if file.endswith("o"):                                                      #if file name does not contain "_opus" then push file
        if '_opus' not in file:
            file_path = os.path.join(path, file)
            get_file_age_in_weeks(file_path)
    ser2.flushInput()
    ser2.flushOutput()
else:
    ser2.flushInput()
    ser2.flushOutput()
    
while shutdown == 'False':                                                  # If SampleDur is 0, no data has come in from datalogger so:
    bytesToRead = ser2.inWaiting()                                          # Check if there are any bytes in the port, assign to "bytesToRead"
    print(bytesToRead)                                                      # Print value in command window
    if bytesToRead == 0:                                                    # If there are no bytes to read:
        ser2.write(b'Run Complete\r')                                       # Send "Run Complete<CR><LF>" out to datalogger to notify the datalogger the PC is done with the script
        ser2.flushInput()                                                   # Flush both inboud and outbound buffers as the "Run Complete" message is now in the dataloggers serial buffer
        ser2.flushOutput()
        time.sleep(60)                                                      # Delay 1 minute before returning to top of While loop as that's the scan rate of datalogger
    else:
        if ShutdownStr == ('Shutdown'):
            shutdown = 'True'
            logging.info('System shutting down')
            ser2.write(b'System shutting down\r')
            print('System shutting down')
            ser2.close()
            time.sleep(5)
            #os.system("shutdown /s /t 1")
        ShutdownStr = ser2.read_until('\n', bytesToRead)                     # If not 0 or > 3 bytes from "inWaiting()", read number of bytes into SampleDur
        ShutdownStr = ShutdownStr.decode("utf-8")
        print(ShutdownStr)
        ser2.flushInput()
        ser2.flushOutput()