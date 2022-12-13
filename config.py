import os

try:

    ComA = 'COM4'
    BaudA = 115200
    ComB = 'COM29'
    BaudB = 115200
    Site = 'Test'
    SiteNumber = '12345678'

    global path

    path = 'C:\\Users\\tviolett\\Documents\\Javad\\' + SiteNumber + '_' + Site + '\\'

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