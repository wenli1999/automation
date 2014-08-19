import logging
import Device
import Util
import pexpect

LOG = logging.getLogger('CLI')

class CliTool(object):
    '''
    CLI Tools for Telnet/SSH access
    '''

    def __init__(self, comm_dict):
        super(CliTool, self).__init__()
        self.nodeIp = comm_dict[Device.CommKey.DEVICE_IP]

        if Device.CommKey.CLI_USER in comm_dict:
            self.username = comm_dict[Device.CommKey.CLI_USER]
        else:
            self.username = Device.Default.USERNAME

        if Device.CommKey.CLI_PASS in comm_dict:
            self.password = comm_dict[Device.CommKey.CLI_PASS]
        else:
            self.password = Device.Default.PASSWORD

        if Device.CommKey.CLI_PASS in comm_dict:
            self.shellPrompt = comm_dict[Device.CommKey.CLI_PASS]
        else:
            self.shellPrompt = Device.Default.PASSWORD

        self.shellPrompt = Device.Default.SHELL_PROMPT

        # expect session
        self.session = None

    def _logSession(self):
        LOG.debug('%s%s', self.session.before, self.session.after)

    def open(self):
        self.session = pexpect.spawn('/usr/bin/telnet {}'.format(self.nodeIp))
        self.session.expect('ogin: ')
        self._logSession()
        self.session.sendline(self.username)
        self.session.expect('assword:')
        self._logSession()
        self.session.sendline(self.password)
        self.session.expect(self.shellPrompt)
        self._logSession()
        self.session.sendline('system shell set more off')
        self.session.expect(self.shellPrompt)
        self._logSession()

    def close(self):
        if self.session != None:
            self.session.sendline('exit')
            self.session.expect('Connection closed by foreign host.')
            self._logSession()

    def sendCommand(self, command, prompt=None):
        self.session.sendline(command)
        if prompt == None:
            prompt = self.shellPrompt
        self.session.expect(prompt)
        self._logSession()
        return self.session.before


def main():
    cliTool = CliTool(Util.parseArgument('CLI unit test'))

    cliTool.open()
    result = cliTool.sendCommand("vlan show")
    LOG.debug('Result: %s', result)
    cliTool.close()


if __name__ == '__main__':
    Util.initLogging()
    main()