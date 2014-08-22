import time
from datetime import datetime
import sys
import signal
import threading
import logging
from pvauto.api import Snmp, Cli, Util, Device


LOG = logging.getLogger(__name__)

SNMP_CHECK_INTERVAL = 5
CLI_WAIT_PRE_REBOOT = 60
CLI_WAIT_DEVICE_DIE = 10
CLI_WAIT_POST_REBOOT = 120

# default output result directory
OUTPUT_DIR = 'RebootTimeResult/'

OIDS = [
    'sysUpTime', '1.3.6.1.2.1.1.3.0',
    'wwpLeosSystemCpuUtilizationLast5Seconds', '1.3.6.1.4.1.6141.2.60.12.1.11.1.0',
    'wwpLeosSystemMemoryUtilizationUsedMemoryCurrent', '1.3.6.1.4.1.6141.2.60.12.1.13.1.0',
    'wwpLeosBladeRunPackageVer', '1.3.6.1.4.1.6141.2.60.10.1.1.3.1.2.1',
    # Leave this one as the last and do not change the name and OID
    'wwpLeosNtpClientSyncState', '1.3.6.1.4.1.6141.2.60.18.1.2.1.0',
]

NTP_STATE_OID = '1.3.6.1.4.1.6141.2.60.18.1.2.1.0'

# Global variables
argDict = {}
stopSign = False


class NtpState:
    INIT = -1
    NO_VALUE = 0
    SYNCED = 1
    UNSYNCED = 2


class NtpStateTracker(object):
    def __init__(self):
        super(NtpStateTracker, self).__init__()
        self.ntpState = NtpState.INIT
        self.ntpRebootTime = -1
        self.ntpUnSyncTime = -1
        self.ntpSyncTime = -1

    def changeStateAndGetTime(self, ntp_state, cur_time):
        # Ignore unchanged state
        if ntp_state == self.ntpState:
            LOG.info('Ignore unchanged state: %s', self)
            return 0

        # Start time tracking from reboot
        if ntp_state == NtpState.NO_VALUE:
            self.ntpState = ntp_state
            self.ntpRebootTime = cur_time
            self.ntpUnSyncTime = -1
            self.ntpSyncTime = -1
            LOG.info('Start time tracking from reboot state: %s', self)
            return 0

        # From reboot to unsynced
        if ntp_state == NtpState.UNSYNCED and self.ntpState == NtpState.NO_VALUE:
            self.ntpState = ntp_state
            self.ntpUnSyncTime = cur_time
            self.ntpSyncTime = -1
            LOG.info('From reboot to unsynced: %s', self)
            return self.ntpUnSyncTime - self.ntpRebootTime

        # From unsync to sync
        if ntp_state == NtpState.SYNCED and self.ntpState == NtpState.UNSYNCED:
            self.ntpState = ntp_state
            self.ntpSyncTime = cur_time
            LOG.info('From unsynced to synced: %s', self)
            return self.ntpSyncTime - self.ntpRebootTime

        # Init case when device is alive, ignore it.
        if (ntp_state == NtpState.SYNCED or ntp_state == NtpState.UNSYNCED) and self.ntpState == NtpState.INIT:
            LOG.debug('Ignore init case')
            return 0

        LOG.error('Unsupported new state: %s; NtpState: %s', ntp_state, self.__str__())
        return 0

    def __str__(self):
        return 'ntpState={}; rebootTime={}; unSyncTime={}; syncTime={}'. \
            format(self.ntpState, self.ntpRebootTime, self.ntpUnSyncTime, self.ntpSyncTime)


class SnmpCheckThread(threading.Thread):
    def __init__(self, arg_dict):
        super(SnmpCheckThread, self).__init__()
        # Save a local copy of reference to reduce global variable use.
        self.argDict = arg_dict

        self.deviceIp = arg_dict[Device.CommKey.DEVICE_IP]
        self.oidNameList = Util.getSubList(OIDS, 0, 2)
        self.oidList = Util.getSubList(OIDS, 1, 2)

        dir = str(arg_dict[Util.ArgKey.OUTPUT_DIR])
        if not dir.endswith('/'):
            dir = dir + '/'

        self.resultFileName = dir + self.deviceIp + '_' + datetime.now().strftime('%Y-%m-%d_%H-%M-%S') + '.csv'

        self.ntpState = NtpStateTracker()

        Util.writeLine(self.resultFileName, self._formHeader())

    def _formHeader(self):
        # Besides OID names, appending two more time related fields
        return '{},Time Stamp,NTP Change Time\n'.format(','.join(self.oidNameList))

    def run(self):
        while not stopSign:
            self._runOnce()
            time.sleep(SNMP_CHECK_INTERVAL)

        LOG.info('Exiting SNMP thread')
        sys.exit(0)

    def _runOnce(self):
        values, cur_ntp_state = self._snmpGetOidValueString()
        cur_time = Util.currentTimeMillis()
        change_time = self.ntpState.changeStateAndGetTime(cur_ntp_state, cur_time)
        Util.writeLine(self.resultFileName, '{}{},{}'.format(values, cur_time, change_time))

    def _snmpGetOidValueString(self):
        snmp_tool = Snmp.SnmpTool(self.argDict)
        ntp_state = NtpState.NO_VALUE
        values = ''
        try:
            result_dict = snmp_tool.snmpGet(self.oidList)
            for oid in self.oidList:
                if oid == NTP_STATE_OID:
                    ntp_state = int(result_dict[oid])
                values = values + result_dict[oid] + ','
        except Snmp.SnmpTimeoutError:
            LOG.info('Timed out when accessing %s', self.deviceIp)
            values = '0,' * (len(OIDS) / 2)

        return values, ntp_state


class CliThread(threading.Thread):
    def __init__(self, arg_dict):
        super(CliThread, self).__init__()
        # Save a local copy of reference to reduce global variable use.
        self.argDict = arg_dict

        self.deviceIp = arg_dict[Device.CommKey.DEVICE_IP]

    def run(self):
        cli = Cli.CliTool(self.argDict)
        cli.open()

        # Pre-reboot wait
        LOG.info('CLI pre-reboot waiting: %ss', CLI_WAIT_PRE_REBOOT)
        time.sleep(CLI_WAIT_PRE_REBOOT)

        # Config save
        LOG.info('Save the config under test')
        cli.sendCommand('config save file current.config')
        cli.sendCommand('tput 192.168.2.6 /SAOS_limitation/current.config current.config')

        # Do reboot
        LOG.info('CLI sending reboot command')
        cli.sendCommand('reboot now', 'Connection closed by foreign host.')

        LOG.info('CLI wait for device die: %ss', CLI_WAIT_DEVICE_DIE)
        time.sleep(CLI_WAIT_DEVICE_DIE)

        # wait device reboot and come back
        LOG.info('CLI waiting for coming back...')
        snmp_tool = Snmp.SnmpTool(self.argDict)
        snmp_tool.snmpWaitForAlive()

        # Re-login
        LOG.info('CLI relogin to device')
        cli.open()

        cli.sendCommand('vlan show')

        # wait after reboot
        LOG.info('CLI post-reboot waiting: %ss', CLI_WAIT_POST_REBOOT)
        time.sleep(CLI_WAIT_POST_REBOOT)

        LOG.info('Exiting Test thread')
        global stopSign
        stopSign = True


def ctrlCHandler(signal, frame):
    LOG.info('Received Ctrl+C, exiting...')
    global stopSign
    stopSign = True
    sys.exit(0)


# Main entrance of this test
def main():
    Util.initLogging()

    global argDict
    argDict = Util.parseArgument('Tracking device reboot time and NTP state change time', OUTPUT_DIR)

    test_thread = CliThread(argDict)
    test_thread.start()

    snmp_thread = SnmpCheckThread(argDict)
    snmp_thread.start()

    # Register to handle Ctrl+C for easy stop
    signal.signal(signal.SIGINT, ctrlCHandler)

    # Program pause and wait for Ctrl+C
    signal.pause()


if __name__ == '__main__':
    main()
