import paramiko
import os
from datetime import datetime
import time
from config import Site, SiteNumber
import logging
from HydroJavad import configure_logger

log_dir = 'D:\\Javad\\' + SiteNumber + '_' + Site + '\\' + wateryear + '\\'
configure_logger(log_dir)
logger = logging.getLogger()

def CheckWY():
    global wateryear
    currentyear = datetime.now().year
    currentmonth = datetime.now().month
    if currentmonth >= 10:
        wy = str(currentyear + 1)
        print(wy)
    else:
        wy = str(currentyear)
        print(wy)
    wateryear = 'WY' + wy
    return(wateryear)

def sftpConnect(path):
    CheckWY()
    for attempt in range(2):
        try:
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            server = 'sftp.usgs.gov'
            port = 22
            user = 'usgs_nsoeder'
            key = 'C:\\Users\\tviolett\\Documents\\sFTP\\usgs_nsoeder\\usgs_nsoeder_openssh'
            ssh_client.connect(server,port,user,key_filename = key,banner_timeout=200,auth_timeout=200)
            ftp = ssh_client.open_sftp()
            ftp.chdir()
            dirs = ftp.listdir()
            sitedirname = SiteNumber + '_' + Site
            active = ssh_client.get_transport().is_active()
            if active == True:
                print('Connection to sftp.usgs.gov is active')
                logging.info('Connection to sftp.usgs.gov is active')
                break
            else:
                print('Connection to sftp.usgs.gov is not active')
                logging.info('Connection to sftp.usgs.gov is not active')
                continue
        except:
            print('Connection to sftp.usgs.gov failed')
            logging.error('Connection to sftp.usgs.gov failed')
            continue

    if active == True:
        if sitedirname in dirs:
            print('Folder Exists, entering folder')
            ftp.chdir(sitedirname)
        else:
            print('Folder does not exist, creating new folder')
            ftp.mkdir(sitedirname)
            ftp.chdir(sitedirname)

        dirs = ftp.listdir()

        if wateryear in dirs:
            print('Folder Exists, entering folder')
            ftp.chdir(wateryear)
            remotepath = ftp.getcwd()
            print(remotepath)
        else:
            print('Folder does not exist, creating new folder')
            ftp.mkdir(wateryear)
            ftp.chdir(wateryear)
            remotepath = ftp.getcwd()
            print(remotepath)

        for file in os.listdir(path):       # For the files in the local directory
            if file.endswith('o'):
                if '_sftp' not in file:
                    ftp.put(path + file,remotepath + '/' + file)
                    file_path = os.path.join(path, file)
                    fn = os.path.splitext(file_path)[0]
                    ext = os.path.splitext(file_path)[1]
                    os.rename(file_path, fn + '_sftp' + ext)
        ftp.close()
        ssh_client.close()
    else:
        logging.error('Connection to sftp.usgs.gov failed, no files uploaded to sftp.usgs.gov')