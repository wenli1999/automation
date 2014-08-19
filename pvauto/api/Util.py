import argparse
import os.path
import time
import logging
import logging.config
import Device


LOG = logging.getLogger(__name__)

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

class ArgKey:
    OUTPUT_DIR = 'OUTPUT_DIR'

def createArgumentParser(description, output_dir=None):
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('--device-ip', help='Device IP address', required=True,
                        dest=Device.CommKey.DEVICE_IP)
    parser.add_argument('--username', help='Telnet/SSH username', default=Device.Default.USERNAME,
                        dest=Device.CommKey.CLI_USER)
    parser.add_argument('--password', help='Telnet/SSH password', default=Device.Default.PASSWORD,
                        dest=Device.CommKey.CLI_PASS)
    parser.add_argument('--snmp-read', help='SNMP read community', default=Device.Default.SNMP_READ_COMM,
                        dest=Device.CommKey.SNMP_READ_COMM)
    parser.add_argument('--snmp-timeout', help='SNMP time out in seconds', default=Device.Default.SNMP_TIME_OUT,
                        dest=Device.CommKey.SNMP_TIME_OUT)
    parser.add_argument('--snmp-retries', help='SNMP retry times', default=Device.Default.SNMP_RETRIES,
                        dest=Device.CommKey.SNMP_RETRIES)
    parser.add_argument('--output-dir', help='Output directory for storing results if any', default=output_dir,
                        dest=ArgKey.OUTPUT_DIR)
    parser.add_argument('--use-ssh', help='SSH Flag indicating using SSH to login', action='store_true',
                        dest=Device.CommKey.CLI_USE_SSH)
    parser.set_defaults(CLI_USE_SSH=False)
    return parser

def parseArgument(description, output_dir=None):
    parser = createArgumentParser(description, output_dir)
    dict = vars(parser.parse_args())
    LOG.info('Input arguments: %s', dict)
    return dict

def initLogging():
    logging.config.fileConfig('logging.ini', disable_existing_loggers=False)
