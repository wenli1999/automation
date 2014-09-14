import time
import sys
import threading
import logging

import Default
from pvauto.api import Snmp, Cli, Util, Device, Argument


LOG = logging.getLogger(Util.getFileBaseName(__file__))

SNMP_CHECK_INTERVAL = 1
WAIT_PRE_ACTION = 60
WAIT_POST_REBOOT = 240

OIDS = [
    'sysUpTime', '1.3.6.1.2.1.1.3.0',
    'wwpLeosSystemCpuUtilizationLast5Seconds', '1.3.6.1.4.1.6141.2.60.12.1.11.1.0',
    'wwpLeosSystemMemoryUtilizationUsedMemoryCurrent', '1.3.6.1.4.1.6141.2.60.12.1.13.1.0',
    'wwpLeosBladeRunPackageVer', '1.3.6.1.4.1.6141.2.60.10.1.1.3.1.2.1',
    # Leave this one as the last and do not change the name and OID
    'wwpLeosNtpClientSyncState', '1.3.6.1.4.1.6141.2.60.18.1.2.1.0',
]

NTP_STATE_OID = '1.3.6.1.4.1.6141.2.60.18.1.2.1.0'

RESULT_DIR = Util.getFileBaseName(__file__) + "_result/"


class NtpState:
    INIT = -1
    NO_VALUE = 0
    SYNCED = 1
    UNSYNCED = 2


class TimeStateTracker(object):
    def __init__(self):
        super(TimeStateTracker, self).__init__()
        self.ntpState = NtpState.INIT
        self.upgradeStartTime = -1
        self.rebootStartTime = -1
        self.ntpUnSyncTime = -1
        self.ntpSyncTime = -1
        self.lastNtpCheckTime = -1
        self.ntpFromUnsyncedToSynced = False

    def startUpgradeTime(self, time):
        self.upgradeStartTime = time

    def isNtpFromUnsyncedToSynced(self):
        return self.ntpFromUnsyncedToSynced

    def changeNtpStateAndGetTime(self, ntp_state, cur_time):
        # return two values: val1, val2
        # val1: NTP change time from last different state
        # val2: download time before reboot

        # Ignore unchanged state
        if ntp_state == self.ntpState:
            # LOG.info('Ignore unchanged state: %s', self)
            self.lastNtpCheckTime = cur_time
            return 0, 0

        # Start time tracking from reboot
        if ntp_state == NtpState.NO_VALUE:
            self.ntpState = ntp_state
            if self.lastNtpCheckTime == -1:
                self.rebootStartTime = cur_time
            else:
                self.rebootStartTime = self.lastNtpCheckTime
            self.ntpUnSyncTime = -1
            self.ntpSyncTime = -1
            LOG.info('Start time tracking from reboot state: %s', self)

            downloadTime = 0
            if self.upgradeStartTime != -1:
                downloadTime = (self.rebootStartTime - self.upgradeStartTime) / 1000

            self.lastNtpCheckTime = cur_time
            return 0, downloadTime

        # From reboot to unSynced
        if ntp_state == NtpState.UNSYNCED and self.ntpState == NtpState.NO_VALUE:
            self.ntpState = ntp_state
            self.ntpUnSyncTime = cur_time
            self.ntpSyncTime = -1
            LOG.info('From reboot to unsynced: %s', self)
            self.lastNtpCheckTime = cur_time
            return (self.ntpUnSyncTime - self.rebootStartTime) / 1000, 0

        # From unsync to sync
        if ntp_state == NtpState.SYNCED and self.ntpState == NtpState.UNSYNCED:
            self.ntpState = ntp_state
            self.ntpSyncTime = cur_time
            LOG.info('From unsynced to synced: %s', self)
            self.lastNtpCheckTime = cur_time
            self.ntpFromUnsyncedToSynced = True
            return (self.ntpSyncTime - self.rebootStartTime) / 1000, 0

        # Init case when device is alive, ignore it.
        if (ntp_state == NtpState.SYNCED or ntp_state == NtpState.UNSYNCED) and self.ntpState == NtpState.INIT:
            # LOG.debug('Ignore init case')
            self.lastNtpCheckTime = cur_time
            return 0, 0

        LOG.error('Unsupported new state: %s; NtpState: %s', ntp_state, self.__str__())
        self.lastNtpCheckTime = cur_time
        return 0, 0

    def __str__(self):
        return 'upgradeStartTime={}; ntpState={}; rebootStartTime={}; ntpUnSyncTime={}; ntpSyncTime={}'. \
            format(self.upgradeStartTime, self.ntpState, self.rebootStartTime, self.ntpUnSyncTime, self.ntpSyncTime)


class SnmpCheckThread(threading.Thread):
    def __init__(self, arg_dict, timeStateTracker):
        super(SnmpCheckThread, self).__init__()
        self.stopSign = False

        # Save a local copy of reference to reduce global variable use.
        self.argDict = arg_dict

        self.deviceIp = arg_dict[Argument.DEVICE_IP[Argument.NAME]]
        self.oidNameList = Util.getSubList(OIDS, 0, 2)
        self.oidList = Util.getSubList(OIDS, 1, 2)

        test_name = str(arg_dict[Argument.TEST_NAME[Argument.NAME]])

        self.resultFileName = RESULT_DIR + self.deviceIp + '_' + test_name + '_' + Util.getTimeStamp() + '.csv'

        self.timeStateTracker = timeStateTracker

        Util.writeLine(self.resultFileName, self._formHeader())

    def _formHeader(self):
        # Besides OID names, appending two more time related fields
        return '{},Time Stamp,NTP Change Time,Download Time\n'.format(','.join(self.oidNameList))

    def stop(self):
        self.stopSign = True

    def run(self):
        while not self.stopSign:
            self._runOnce()
            time.sleep(SNMP_CHECK_INTERVAL)

        LOG.info('Exiting SNMP thread')

    def _runOnce(self):
        values, cur_ntp_state = self._snmpGetOidValueString()
        cur_time = Util.currentTimeMillis()
        change_time, download_time = self.timeStateTracker.changeNtpStateAndGetTime(cur_ntp_state, cur_time)
        Util.writeLine(self.resultFileName, '{}{},{},{}'.format(values, cur_time, change_time, download_time))

    def _snmpGetOidValueString(self):
        snmp_tool = Snmp.SnmpTool(self.argDict)
        ntp_state = NtpState.NO_VALUE
        values = ''
        try:
            result_dict = snmp_tool.snmpGetList(self.oidList)
            for oid in self.oidList:
                if oid == NTP_STATE_OID:
                    ntp_state = int(result_dict[oid])
                values = values + result_dict[oid] + ','
        except Snmp.SnmpTimeoutError:
            LOG.info('Timed out when accessing %s', self.deviceIp)
            values = '0,' * (len(OIDS) / 2)

        return values, ntp_state


def validateVersionUpgrade(device, upgrade_version):
    device.refresh()
    if upgrade_version != device.getSoftwareVersion():
        error_message = 'Failed to upgrade to target version [%s], device still running [%s]' \
                        % (upgrade_version, device.getSoftwareVersion())
        LOG.error(error_message)
        raise StandardError(error_message)

    LOG.info('Device successfully upgraded to version: [%s]', upgrade_version)


# Main entrance of this test
def main():
    Util.initLogging()

    arg_dict = Argument.parseArgument('Tracking device reboot time and NTP state change time', Default.defaultDict)

    start_time = Util.currentTimeMillis()

    device = Device.Device(arg_dict)
    LOG.info('%s: Starting test...', device.getIp())
    LOG.info('%s: Device current version: [%s]', device.getIp(), device.getSoftwareVersion())

    # timeStateTracker = TimeStateTracker()
    # LOG.info('Start SNMP checking thread')
    # snmp_thread = SnmpCheckThread(arg_dict, timeStateTracker)
    # snmp_thread.start()
    # time.sleep(60)

    cli = Cli.CliTool(arg_dict)
    cli.open()

    save_config = "backup_" + Util.getTimeStamp() + ".config"
    tftp_server = arg_dict.get(Argument.TFTP_SERVER[Argument.NAME])
    remote_config = Default.ipToConfigDict.get(device.getIp())
    LOG.info('%s: Save current config to [%s] and download baseline config [%s] from TFTP server [%s]',
             device.getIp(), save_config, remote_config, tftp_server)
    cli.sendCommands(
        'conf save file ' + save_config,
        'cd /mnt/sysfs/config',
        'tget ' + tftp_server + ' ' + remote_config + ' startup-config'
    )

    base_version = arg_dict.get(Argument.SAOS_VERSION1[Argument.NAME])
    final_version = arg_dict.get(Argument.SAOS_VERSION2[Argument.NAME])
    if base_version != device.getSoftwareVersion():
        LOG.info('%s: Upgrade from current version [%s] to base version [%s], reboot...',
                 device.getIp(), device.getSoftwareVersion(), base_version)
        device.rebootAndReLogin(cli, 'software upgrade package ' + base_version +
                                ' server ' + tftp_server + ' service-disruption all')
    else:
        LOG.info('%s: Device already running base version [%s], reboot...', device.getIp(), base_version)
        device.rebootAndReLogin(cli, 'reboot now')

    validateVersionUpgrade(device, base_version)

    timeStateTracker = TimeStateTracker()
    LOG.info('%s: Start SNMP checking thread', device.getIp())
    snmp_thread = SnmpCheckThread(arg_dict, timeStateTracker)
    snmp_thread.start()

    cli.sendCommand('software show')

    LOG.info('Pre-action waiting: %ss', WAIT_PRE_ACTION)
    time.sleep(WAIT_PRE_ACTION)

    # Set upgrade start time
    timeStateTracker.startUpgradeTime(Util.currentTimeMillis())

    LOG.info('%s: Upgrade from base version [%s] to final version [%s]', device.getIp(), base_version, final_version)
    device.rebootAndReLogin(cli, 'software upgrade package ' + final_version +
                            ' server ' + tftp_server + ' service-disruption all')

    validateVersionUpgrade(device, final_version)

    cli.sendCommand('software show')

    # wait after reboot
    ntp_sync_start_wait = Util.currentTimeMillis()
    ntp_synced = True
    ntp_sync_total_wait = 0
    while not timeStateTracker.isNtpFromUnsyncedToSynced():
        time.sleep(2)
        ntp_sync_total_wait = (Util.currentTimeMillis() - ntp_sync_start_wait) / 1000
        if ntp_sync_total_wait > WAIT_POST_REBOOT:
            ntp_synced = False
            break

    if ntp_synced:
        LOG.info('%s: NTP synced after %ss', device.getIp(), ntp_sync_total_wait)
    else:
        LOG.error('%s: Failed to wait NTP synced after timeout %ss', device.getIp(), ntp_sync_total_wait)

    cli.close()

    LOG.info('%s: Stop SNMP thread', device.getIp())
    snmp_thread.stop()

    LOG.info('%s: Ending test, total time: %s', device.getIp(), (Util.currentTimeMillis() - start_time) / 1000)
    sys.exit(0)


if __name__ == '__main__':
    main()
