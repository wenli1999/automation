import time
import logging

import Snmp
import Argument
import Util


LOG = logging.getLogger(Util.getFileBaseName(__file__))

class Default:
    SHELL_PROMPT = '> '


class Device(object):
    def __init__(self, comm_dict):
        super(Device, self).__init__()
        self.deviceIp = comm_dict[Argument.DEVICE_IP[Argument.NAME]]
        self.snmp = Snmp.SnmpTool(comm_dict)
        self.softwareVersion = None

    def getIp(self):
        return self.deviceIp

    def refresh(self):
        self.softwareVersion = None

    def getSoftwareVersion(self):
        if self.softwareVersion == None:
            result_dict = self.snmp.snmpGet('1.3.6.1.4.1.6141.2.60.10.1.1.3.1.2.1')
            for key, value in result_dict.items():
                self.softwareVersion = value
        return self.softwareVersion

    def snmpCheckAlive(self):
        try:
            self.snmp.snmpGet('1.3.6.1.2.1.1.1.0')
            return True
        except Snmp.SnmpTimeoutError:
            return False

    def snmpWaitForAlive(self, interval=2):
        alive = self.snmpCheckAlive()
        while not alive:
            time.sleep(interval)
            alive = self.snmpCheckAlive()
        LOG.info('%s: Device is alive', self.deviceIp)

    def snmpWaitForDown(self, interval=2):
        alive = self.snmpCheckAlive()
        while alive:
            time.sleep(interval)
            alive = self.snmpCheckAlive()
        LOG.info('%s: Device is down', self.deviceIp)

    def rebootAndReLogin(self, cli, command):
        cli.sendCommandNoWait(command)

        LOG.info('%s: Wait for device down...', self.deviceIp)
        self.snmpWaitForDown()

        cli.close(True)

        # Wait device reboot and come back
        LOG.info('%s: Wait for device alive...', self.deviceIp)
        self.snmpWaitForAlive()

        # Re-login
        LOG.info('%s: Re-log into device', self.deviceIp)
        cli.open()
