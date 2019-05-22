import datetime
import logging
import os


def loggingSetter(loggingLevel, loggingPrint, loggingSaveOutput):
    '''This is what the logging level and output during the write operation.  It's worth nothing that this is the ONLY
    function that checks parameters outside of verifyWriteParameters, because that function's logging outputs hinge in
    the configuration for logging.
    '''

    # First, we're checking the parameters are valid.
    acceptableLevelWords = [False, 'debug', 'info']
    if loggingLevel not in acceptableLevelWords:
        raise ValueError(f"{loggingLevel} is not a valid input for loggingLevel.  Only 'info', 'debug', and False are "
                         f"allowed.")

    if not isinstance(loggingPrint, bool):
        raise ValueError("Only booleans are allowed for loggingPrint.")

    if not isinstance(loggingSaveOutput, bool):
        raise ValueError("Only booleans are allowed for loggingSaveOutput.")

    loggingLevelDict = {False: None, 'debug': logging.DEBUG, 'info': logging.INFO}

    # Next, we're setting each of the loggers if they are enabled.
    if loggingSaveOutput:

        if not os.path.isdir('logs'):
            os.mkdir('logs')
        logOutputName= f"logs\\{datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S')}.txt"
        outputLog = logging.getLogger()
        outputLogHandler = logging.FileHandler(logOutputName)
        outputLogFormatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
        outputLogHandler.setFormatter(outputLogFormatter)
        outputLog.addHandler(outputLogHandler)
        outputLog.setLevel(loggingLevelDict[loggingLevel])

    if loggingPrint:

        printLog = logging.getLogger()
        printLogHandler = logging.StreamHandler()
        printLogFormatter = logging.Formatter("%(asctime)s.%(msecs)03d %(levelname)s %(message)s", "%H:%M:%S")
        printLogHandler.setFormatter(printLogFormatter)
        printLog.addHandler(printLogHandler)
        printLog.setLevel(loggingLevelDict[loggingLevel])