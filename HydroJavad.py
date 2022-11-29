import sys

sys.path.insert(0,'C:\\Users\\Trevor\\Desktop\\HydroJavadPy\\')

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import logging
import serial
from config import ComA, BaudA, ComB, BaudB, Site, SiteNumber, User
import time
from datetime import datetime
import os
import shutil
import ftplib
import sftp
from OPUSh import push_file, get_file_age_in_weeks

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
        alert = driver.switch_to.alert
        alert.accept()
        print("alert accepted")
    except:
        print("no alert")
    try:
        alert = driver.switch_to.alert
        alert.accept()
        print("alert accepted")
    except:
        print("no alert")
    try:
        alert = driver.switch_to.alert
        alert.accept()
        print("alert accepted")
        logging.info(file_path + ' File name unrecognized')
    except:
        print("no alert")
    
    #read text from next webpage
    time.sleep(5)
    text = driver.find_element(By.ID, 'container').text
    print(text)
    #if text contains "upload successful" then remove extension from filename
    if 'Upload successful' in text:
        logging.info(file_path + ' Uploaded successfully to OPUS.')
        file = os.path.splitext(file_path)[0]
        ext = os.path.splitext(file_path)[1]
        os.rename(file_path, file + '_uploaded' + ext)
        logging.info('File has been renamed')
    else:
        logging.info(file_path + ' Upload to OPUS unsuccessful.')
        #store error to log file
        logging.error(text)
    driver.close()

global path

currentmonth = datetime.now().month
wateryear = sftp.CheckWY()

path = 'C:\\Users\\' + User + '\\Documents\\Javad\\' + SiteNumber + '_' + Site + '\\' + wateryear + '\\'                # Define path for data storage
newpath = 1
msg = ''
sitedirname = SiteNumber + '_' + Site


try:                                                                        # Try to make the path by making new directory
    os.makedirs(path)
    newpath = -1
except OSError as error:                                                    # If path already exists
    print(error)                                                           # Print the error message
    msg = error
    newpath = 0


logfile = os.path.join(path, datetime.now().strftime('sample_%Y%m%d-%H%M')+".log")
FORMAT = "%(asctime)s — %(name)s — %(levelname)s — %(funcName)s:%(lineno)d — %(message)s"
logging.basicConfig(filename=logfile, format=FORMAT)
logger = logging.getLogger()
logger.setLevel(level=logging.INFO)

if newpath == -1:
    logging.info('New directory created.')
else:
    logging.info(msg)


timestr = time.strftime("%Y%m%d_%H%M")  #opus won't accept hyphens in file name 
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


while SampleDur == 0 and (SampleGNSS != 0 or SampleGNSS != -1):                                                       # If SampleDur is 0, no data has come in from datalogger so:
    bytesToRead = ser2.inWaiting()                                          # Check if there are any bytes in the port, assign to "bytesToRead"
    print(bytesToRead)                                                      # Print value in command window
    if bytesToRead == 0:                                                    # If there are no bytes to read:
        ser2.write(b'Ready\r')                                            # Send "Ready<CR><LF>" out to datalogger to notify the datalogger the PC is ready to run the script
        ser2.flushInput()                                                   # Flush both inboud and outbound buffers as the "Ready" message is now in the dataloggers serial buffer
        ser2.flushOutput()
        time.sleep(60)                                                      # Delay 1 minute before returning to top of While loop as that's the scan rate of datalogger
    #elif bytesToRead > 3:                                                   # If we have more than 3 bytes, there are likely junk bytes. Expecting 12hr sampling (720 minutes)
       # ser2.flushInput()                                                   # Flush ports
        #ser2.flushOutput()
        #time.sleep(60)                                                      # Delay 1 minute before returning to top of While loop
    else:
        TestStr = ser2.read_until('\n', bytesToRead)                                  # If not 0 or > 3 bytes from "inWaiting()", read number of bytes into SampleDur
        print(TestStr) #SampleDur = int(SampleDur)
        TestStr = TestStr.decode("utf-8")
        if TestStr.startswith('SID'):
            splitdata = TestStr.split(",") # Change variable from tyep Bytes to type Integer
            print(splitdata)                                                    # Print value to know how many bytes are expected
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
    fn = SiteNumber + "_" + Site + "_Javad_"                                                           # Define site ID for file naming -- Do this via communication to datalogger?
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
    while time.time() < t_end:                                                  # While current time is less than end time
        bytesToRead = ser.inWaiting()                                           # Check buffer for bytes available
        print(bytesToRead)                                                      # Print how many bytes are in buffer
        rl = ser.read(bytesToRead)                                              # Read number of bytes in buffer to "rl"
        print(rl)                                                               # Print the bytes
        file.write(rl)                                                          # Write the bytes to the open .jps file
        time.sleep(2)                                                           # Delay 2 sec to ensure next message(s) are there for continuing While loop

    file.close()                                                                # After While loop finishes
    ser.write(bytes(b'dm,,/msg/def\r\n'))                                       # Send "disable message output" command to Javad
    time.sleep(1)                                                               # Delay 1 second
    ser.close()                                                                 # Close both serial port A
    os.system(cmdstr)                                                           # Output the command-line command to convert .jps to RINEX

    numfiles = len([name for name in os.listdir(path) if name.endswith('o')]) # Check directory for files ending in "o" (indicating OPUS file), store the count in "numfiles"
    print(numfiles)
    numFiles = str(numfiles)
    logging.info(numFiles + ' files to push to FTP.')                                         # Print the number of OPUS files
    if numfiles >= 1:                                                            # If more than X -- perhaps always send after every sample period instead of waiting for multiple files? Unless user starts manually?
        sftp.sftpConnect(path)
        

for file in os.listdir(path):
    if file.endswith("o"):
        #if file name does not contain "_uploaded" then push file
        if '_uploaded' not in file:
            file_path = os.path.join(path, file)
            get_file_age_in_weeks(file_path)

    print('Run Complete')                                                      # Run Complete
    logging.info("Run Complete.")
    ser2.flushInput()
    ser2.flushOutput()
else:
    ser2.flushInput()
    ser2.flushOutput()
    
while shutdown == 'False':                                                       # If SampleDur is 0, no data has come in from datalogger so:
    bytesToRead = ser2.inWaiting()                                          # Check if there are any bytes in the port, assign to "bytesToRead"
    print(bytesToRead)                                                      # Print value in command window
    if bytesToRead == 0:                                                    # If there are no bytes to read:
        ser2.write(b'Run Complete\r')                                            # Send "Ready<CR><LF>" out to datalogger to notify the datalogger the PC is ready to run the script
        ser2.flushInput()                                                   # Flush both inboud and outbound buffers as the "Ready" message is now in the dataloggers serial buffer
        ser2.flushOutput()
        time.sleep(60)                                                      # Delay 1 minute before returning to top of While loop as that's the scan rate of datalogger
    #elif bytesToRead > 3:                                                   # If we have more than 3 bytes, there are likely junk bytes. Expecting 12hr sampling (720 minutes)
       # ser2.flushInput()                                                   # Flush ports
        #ser2.flushOutput()
        #time.sleep(60)                                                      # Delay 1 minute before returning to top of While loop
    else:
        ShutdownStr = ser2.read_until('\n', bytesToRead)                     # If not 0 or > 3 bytes from "inWaiting()", read number of bytes into SampleDur
        ShutdownStr = ShutdownStr.decode("utf-8")
        print(ShutdownStr) #SampleDur = int(SampleDur)
        ser2.flushInput()
        ser2.flushOutput()
        if ShutdownStr == ('Shutdown'):
            shutdown = 'True'
            ser2.close()
            logging.info('System shutting down')
            print('System shutting down')
            time.sleep(5)
            #os.system("shutdown /s /t 1")


