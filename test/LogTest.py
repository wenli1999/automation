__author__ = 'jingli'

import logging
import logging.config

class LogTest(object):

    def __init__(self):
        super(LogTest, self).__init__()
        self.logger = logging.getLogger(__name__)

    def run(self):
        self.logger.info('Start reading database')
        # read database here

        records = {'john': 55, 'tom': 66}
        self.logger.debug('Records: %s', records)
        self.logger.info('Updating records ...')
        # update records here

        self.logger.info('Finish updating records')

class LogTest2(object):

    def __init__(self):
        super(LogTest2, self).__init__()
        self.logger = logging.getLogger('LogTest2')

    def run(self):
        self.logger.info('Start reading database')
        # read database here

        records = {'john': 55, 'tom': 66}
        self.logger.debug('Records: %s', records)
        self.logger.info('Updating records ...')
        # update records here

        self.logger.info('Finish updating records')

def main():
    logging.config.fileConfig('logging.ini')

    for i in range(0, 1000):
        LogTest().run()
        LogTest2().run()

if __name__ == '__main__':
    main()
