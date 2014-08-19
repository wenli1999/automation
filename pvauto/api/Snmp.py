from subprocess import PIPE, Popen
import time
import logging
import Device
import Util



LOG = logging.getLogger('SNMP')

class SnmpTool(object):
    '''
    SNMP Tools for SNMP V2c access
    '''

    def __init__(self, comm_dict):
        super(SnmpTool, self).__init__()
        self.deviceIp = comm_dict[Device.CommKey.DEVICE_IP]

        if Device.CommKey.SNMP_READ_COMM in comm_dict:
            self.readComm = comm_dict[Device.CommKey.SNMP_READ_COMM]
        else:
            self.readComm = Device.Default.SNMP_READ_COMM

        if Device.CommKey.SNMP_TIME_OUT in comm_dict:
            self.timeout = comm_dict[Device.CommKey.SNMP_TIME_OUT]
        else:
            self.timeout = Device.Default.SNMP_TIME_OUT

        if Device.CommKey.SNMP_RETRIES in comm_dict:
            self.retries = comm_dict[Device.CommKey.SNMP_RETRIES]
        else:
            self.timeout = Device.Default.SNMP_TIME_OUT

    def _parseSnmpResult(self, output, error):
        '''
        Parsing raw SNMP output in multiple columns formats separated by spaces
        :param error: Raw stderr output result string
        :param output: Raw SNMP output string
        :return: A dictionary
        '''

        if output != None or len(output) == 0:
            LOG.debug('%s', output)
        if error != None or len(output) == 0:
            LOG.debug('%s', error)

        # Process timeout case first
        # Timeout: No Response from
        if error.startswith('Timeout:'):
            raise SnmpTimeoutError

        resultDict = {}

        for aLine in output.splitlines():
            newLine = aLine.strip()
            firstSpaceIndex = newLine.index(' ')
            key = newLine[0:firstSpaceIndex]
            value = newLine[firstSpaceIndex + 1:]
            if value.startswith('"') and value.endswith('"'):
                value = value[1:-1]
            if key.startswith('.'):
                key = key[1:]
            resultDict[key] = value

        return resultDict

    def snmpBulkWalk(self, oid):
        cmd = '/usr/bin/snmpbulkwalk -v 2c -Oqn -t {} -r {} -c {} {} {}'. \
            format(self.timeout, self.retries, self.readComm, self.deviceIp, oid)
        LOG.debug('%s', cmd)

        p = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
        output, error = p.communicate()

        return self._parseSnmpResult(output, error)

    def snmpGet(self, oidList):
        cmd = '/usr/bin/snmpget -v 2c -Oqn -t {} -r {} -c {} {} {}'. \
            format(self.timeout, self.retries, self.readComm, self.deviceIp, ' '.join(oidList))
        LOG.debug('%s', cmd)

        p = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
        output, error = p.communicate()

        return self._parseSnmpResult(output, error)

    def snmpCheckAlive(self):
        try:
            self.snmpGet(['1.3.6.1.2.1.1.1.0'])
            return True
        except SnmpTimeoutError:
            return False

    def snmpWaitForAlive(self, interval=2):
        alive = self.snmpCheckAlive()
        while not alive:
            time.sleep(interval)
            alive = self.snmpCheckAlive()


class SnmpTimeoutError(Exception):
    '''
    Indicating SNMP timeout
    '''
    pass


class SnmpGeneralError(Exception):
    '''
    Indicating SNMP general error
    '''
    pass


def main():
    snmpTool = SnmpTool(Util.parseArgument('SNMP unit test'))

    # Check alive blocking
    snmpTool.snmpWaitForAlive()

    # getBulk
    result = snmpTool.snmpBulkWalk(oid='1.3.6.1.4.1.6141.2.60.2.1.1.1.1.2')
    for key, value in result.items():
        LOG.debug('%s = %s', key, value)

    # get
    result = snmpTool.snmpGet(oidList=['1.3.6.1.2.1.1.1.0', '1.3.6.1.2.1.1.5.0', '1.3.6.1.4.1.6141.2.60.12.1.11.1.0',
                                       '1.3.6.1.4.1.6141.2.60.2.1.1.1.1.2.1'])
    for key, value in result.items():
        LOG.debug('%s = %s', key, value)

if __name__ == '__main__':
    Util.initLogging()
    main()