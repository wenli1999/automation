import argparse
import logging

import Util


LOG = logging.getLogger(Util.getFileBaseName(__file__))

NAME = 0
HELP = 1
REQUIRED = 2
DEFAULT = 3

DEVICE_IP = ['device-ip', 'Device IP address', True, None]
SNMP_READ_COMM = ['snmp-read', 'SNMP read community', False, 'public']
SNMP_TIME_OUT = ['snmp-timeout', 'SNMP timeout in seconds', False, 10]
SNMP_RETRIES = ['snmp-retries', 'SNMP retries', False, 0]
CLI_USER = ['username', 'Telnet/SSH username', False, 'su']
CLI_PASS = ['password', 'Telnet/SSH password', False, 'wwp']
TEST_NAME = ['test-name', 'Name of the current test', False, '']
TFTP_SERVER = ['tftp-server', 'TFTP server IP', False, None]
REMOTE_FILE = ['remote-file', 'Remote file name on TFTP server', False, None]
SAOS_VERSION1 = ['saos-verison1', 'SAOS version string 1', False, None]
SAOS_VERSION2 = ['saos-verison2', 'SAOS version string 2', False, None]

ALL = [
    DEVICE_IP,
    CLI_USER,
    CLI_PASS,
    SNMP_READ_COMM,
    SNMP_TIME_OUT,
    SNMP_RETRIES,
    TEST_NAME,
    TFTP_SERVER,
    REMOTE_FILE,
    SAOS_VERSION1,
    SAOS_VERSION2,
]


def createArgumentParser(description, custom_default_dict={}):
    parser = argparse.ArgumentParser(description=description)

    for arg_list in ALL:
        default_value = arg_list[DEFAULT]
        if arg_list[NAME] in custom_default_dict:
            default_value = custom_default_dict.get(arg_list[NAME])
        parser.add_argument('--' + arg_list[NAME], help=arg_list[HELP], required=arg_list[REQUIRED],
                            dest=arg_list[NAME], default=default_value)
        LOG.debug("Building argument with default: %s=%s", arg_list[NAME], default_value)

    return parser


def parseArgument(description, custom_default_dict={}):
    parser = createArgumentParser(description, custom_default_dict)
    dict = vars(parser.parse_args())
    LOG.info('Input arguments: %s', dict)
    return dict
