import paramiko
import os
from datetime import datetime
from config import Site, SiteNumber



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
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    server = 'sftp.usgs.gov'
    port = 22
    user = 'usgs_nsoeder'
    key = 'C:\\Users\\tviolett\\Documents\\sFTP\\usgs_nsoeder\\usgs_nsoeder_openssh'
    ssh_client.connect(server,port,user,key_filename = key)
    ftp = ssh_client.open_sftp()

    ftp.chdir()
    dirs = ftp.listdir()
    sitedirname = SiteNumber + '_' + Site

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

    for files in os.listdir(path):       # For the files in the local directory
        if files.endswith('o'):
            ftp.put(path + files,remotepath + '/' + files)
    ftp.close()