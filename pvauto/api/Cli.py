import logging

import pexpect

import Util
import Argument
import Device

LOG = logging.getLogger('CLI')

class CliTool(object):
    '''
    CLI Tools for Telnet/SSH access
    '''

    def __init__(self, comm_dict):
        super(CliTool, self).__init__()
        self.nodeIp = comm_dict[Argument.DEVICE_IP[Argument.NAME]]
        self.username = comm_dict[Argument.CLI_USER[Argument.NAME]]
        self.password = comm_dict[Argument.CLI_PASS[Argument.NAME]]
        self.shellPrompt = Device.Default.SHELL_PROMPT

        # expect session
        self.session = None

    def _logSession(self):
        LOG.debug('%s: %s%s', self.nodeIp, self.session.before, self.session.after)

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

    def close(self, force=False):
        LOG.debug('%s: Closing session...', self.nodeIp)
        if self.session == None:
            return

        if (not force) and self.session.isalive():
            self.session.sendline('exit')
            self.session.expect('Connection closed by foreign host.')
            self._logSession()

        self.session.close(True)

    def sendCommand(self, command, prompt=None):
        LOG.debug('%s: Sending command: %s', self.nodeIp, command)
        self.session.sendline(command)
        if prompt == None:
            prompt = self.shellPrompt
        self.session.expect(prompt)
        self._logSession()
        return self.session.before

    def sendCommands(self, *commands):
        for command in commands:
            self.sendCommand(command)

    def sendCommandNoWait(self, command):
        LOG.debug('%s: Sending command without wait: %s', self.nodeIp, command)
        self.session.sendline(command)


def main():
    arg_dict = Argument.parseArgument('CLI unit test')
    cliTool = CliTool(arg_dict)

    cliTool.open()
    cliTool.sendCommand("vlan show")
    cliTool.close()

    cliTool.open()
    cliTool.sendCommand("port show")
    cliTool.close()

    cliTool.open()
    device = Device.Device(arg_dict)
    device.rebootAndReLogin(cliTool, 'reboot now')
    cliTool.sendCommand('int show')
    cliTool.close()


if __name__ == '__main__':
    Util.initLogging()
    main()