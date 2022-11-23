#get file age in weeks
from datetime import datetime
import os
import OPUSh
path = 'C:\\Users\\tviolett\\Documents\\Javad\\'

#if file is older than 2 weeks, return file path
def get_file_age_in_weeks(file_path):
    #file_path = os.path.join(path, file)
    file_time = os.path.getmtime(file_path)
    file_age = datetime.now().timestamp() - file_time
    file_age_weeks = file_age/604800
    print(file_age_weeks)
    if file_age_weeks >= 2:
        print('File is older than 2 weeks')
        print(file_path)
        #push_file(file_path)
        print('File has been pushed')
    else:
        print('File is younger than 2 weeks')
        print(file_path)
        print('File has not been pushed')


for file in os.listdir(path):
    if file.endswith("o"):
        file_path = os.path.join(path, file)
        get_file_age_in_weeks(file_path)