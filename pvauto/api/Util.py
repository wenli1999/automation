import os.path
import time
import logging
import logging.config
from datetime import datetime


def getFileBaseName(file):
    name = os.path.basename(file)
    return name[0:name.rfind('.py')]


LOG = logging.getLogger(getFileBaseName(__file__))

def getSubList(list, startIndex, step):
    resultList = []
    for i in xrange(startIndex, len(list), step):
        resultList.append(list[i])

    return resultList

def writeLine(filePath, line=''):
    if not line.endswith('\n'):
        line = line + '\n'

    parentDir = os.path.abspath(os.path.join(filePath, os.path.pardir))
    if not os.path.exists(parentDir):
        os.makedirs(parentDir)
        LOG.info('Created parent directory: %s', parentDir)

    with open(filePath, 'a') as fileHandle:
        fileHandle.write(line)

    LOG.debug('%s: added a line: %s', filePath, line)

def currentTimeMillis():
    return int(round(time.time() * 1000))


def getTimeStamp():
    return datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

def initLogging():
    logging.config.fileConfig('logging.ini', disable_existing_loggers=False)
