import os

try:
    import sys

    sys.path.insert(0,'C:\\Users\\tviolett\\Documents\\GitLab\\HydroJavadPy\\')

    import logging
    from datetime import datetime
    import config

    # def CheckWY():
    #     global wateryear
    #     currentyear = datetime.now().year
    #     currentmonth = datetime.now().month
    #     if currentmonth >= 10:
    #         wy = str(currentyear + 1)
    #         print(wy)
    #     else:
    #         wy = str(currentyear)
    #         print(wy)
    #     wateryear = 'WY' + wy
    #     return(wateryear)

    # wateryear = None
    # wateryear = CheckWY()

    # path = os.path.join(path, wateryear)

    config.make_directory()

    datetime = datetime.now()


    def configure_logger(path):
        # Set the log file path
        logfile = os.path.join(path, datetime.now().strftime('sample_%Y%m%d-%H%M')+".log")

        # Set the log format
        FORMAT = "%(asctime)s — %(name)s — %(levelname)s — %(funcName)s:%(lineno)d — %(message)s"

        # Configure the logger
        logging.basicConfig(filename=logfile, format=FORMAT)
        logger = logging.getLogger()
        logger.setLevel(level=logging.INFO)
except Exception as error:
    print(error)
    msg = error
    print('Unknown error')
    input()