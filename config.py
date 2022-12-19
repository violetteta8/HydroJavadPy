import os

try:

    ComA = 'COM3'
    BaudA = 115200
    ComB = 'COM1'
    BaudB = 115200
    Site = 'Test'
    SiteNumber = '12345678'

    global path

    path = 'D:\\Javad\\' + SiteNumber + '_' + Site + '\\'

    try:                                                                        # Try to make the path by making new directory
        os.makedirs(path)
        newpath = -1
    except OSError as error:                                                    # If path already exists
        print(error)                                                           # Print the error message
        msg = error
except Exception as error:
    print(error)
    msg = error
    print('Unknown error')
    input()