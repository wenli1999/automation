from subprocess import PIPE, Popen
import logging

import Util
import Argument


LOG = logging.getLogger('SNMP')

class SnmpTool(object):
    '''
    SNMP Tools for SNMP V2c access
    '''

    def __init__(self, comm_dict):
        super(SnmpTool, self).__init__()
        self.deviceIp = comm_dict[Argument.DEVICE_IP[Argument.NAME]]
        self.readComm = comm_dict[Argument.SNMP_READ_COMM[Argument.NAME]]
        self.timeout = comm_dict[Argument.SNMP_TIME_OUT[Argument.NAME]]
        self.retries = comm_dict[Argument.SNMP_RETRIES[Argument.NAME]]

    def _parseSnmpResult(self, output, error):
        '''
        Parsing raw SNMP output in multiple columns formats separated by spaces
        :param error: Raw stderr output result string
        :param output: Raw SNMP output string
        :return: A dictionary
        '''

        if output != None:
            output = output.strip()
            if len(output) > 0:
                LOG.debug('%s', output)
        if error != None:
            error = error.strip()
            if len(error) > 0:
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

    def snmpGet(self, *oids):
        return self.snmpGetList(oids)

    def snmpGetList(self, oid_list):
        cmd = '/usr/bin/snmpget -v 2c -Oqn -t {} -r {} -c {} {} {}'. \
            format(self.timeout, self.retries, self.readComm, self.deviceIp, ' '.join(oid_list))
        LOG.debug('%s', cmd)

        p = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
        output, error = p.communicate()

        return self._parseSnmpResult(output, error)

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
    snmpTool = SnmpTool(Argument.parseArgument('SNMP unit test'))

    # getBulk
    result = snmpTool.snmpBulkWalk('1.3.6.1.4.1.6141.2.60.2.1.1.1.1.2')
    for key, value in result.items():
        LOG.debug('%s = %s', key, value)

    # get
    result = snmpTool.snmpGet('1.3.6.1.2.1.1.1.0', '1.3.6.1.2.1.1.5.0', '1.3.6.1.4.1.6141.2.60.12.1.11.1.0',
                              '1.3.6.1.4.1.6141.2.60.2.1.1.1.1.2.1')
    for key, value in result.items():
        LOG.debug('%s = %s', key, value)

    # Get list
    oid_list = ['1.3.6.1.2.1.1.1.0', '1.3.6.1.2.1.1.5.0', '1.3.6.1.4.1.6141.2.60.12.1.11.1.0',
                '1.3.6.1.4.1.6141.2.60.2.1.1.1.1.2.1']
    result = snmpTool.snmpGetList(oid_list)
    for key, value in result.items():
        LOG.debug('%s = %s', key, value)


if __name__ == '__main__':
    Util.initLogging()
    main()