import os
from datetime import datetime

try:

    ComA = 'COM4'
    BaudA = 115200
    ComB = 'COM29'
    BaudB = 115200
    Site = 'Test'
    SiteNumber = '12345678'

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

    def make_directory():
        global path
        CheckWY()
        path = 'C:\\Users\\tviolett\\Documents\\Javad\\' + SiteNumber + '_' + Site + '\\' + wateryear
        try:                                                                        # Try to make the path by making new directory
            os.makedirs(path)
            newpath = -1
        except OSError as error:                                                    # If path already exists
            print(error)                                                           # Print the error message
            msg = error
        return (path)

except Exception as error:
    print(error)
    msg = error
    print('Unknown error')
    input()