#!/usr/bin/python3
# -*- coding:utf-8 -*-

###############################################################################
# Sample Python script which run as a background process.
#
# The process terminates when it finishes its works. Use "stop" parameter to
# force to stop immediately. Use a unique id as an argument to run multiple
# instances.
#
# Usage:
#       myproc.py start|stop|restart uniqid
#
###############################################################################

import os
import sys
import time
import atexit
import argparse
from   mydaemon import Daemon

# Daemon name. It's only used in messages.
DAEMON_NAME = 'My Background Process (id: #ID#)'
# Cleanstop wait time before to kill the process.
DAEMON_STOP_TIMEOUT = 10
# Daemon pid file.
PIDFILE = '/tmp/myproc_#ID#.pid'
# Deamon run file. "stop" request deletes this file to inform the process and
# waits DAEMON_STOP_TIMEOUT seconds before to send SIGTERM. The process has a
# change to stop cleanly if it's written appropriately.
RUNFILE = '/tmp/myproc_#ID#.run'
# Debug mode.
DEBUG = 0



# -----------------------------------------------------------------------------
def get_args():
    '''
    >>> get_args()
    ('start', 5)
    >>> get_args()
    ('stop', 4)
    '''

    try:
        parser =  argparse.ArgumentParser()
        parser.add_argument('action', help='action',
                            choices=['start', 'stop', 'restart'])
        parser.add_argument('uniqid', help='Unique ID')
        args = parser.parse_args()

        result = (args.action, args.uniqid)
    except Exception as err:
        if DEBUG:
            raise
        else:
            sys.stderr.write('%s\n' % (err))

        result = (None, None)

    return result



# -----------------------------------------------------------------------------
class MyProc(Daemon):
    def run(self):
        '''
        Process start to run here.
        '''

        # Delete the run file at exit. Maybe there will be no stop request.
        atexit.register(self.delrun)

        # Run while there is no stop request.
        n = 0
        while os.path.exists(RUNFILE):
            print('.')
            n += 1

            if (n > 60):
                break

            time.sleep(1)



# -----------------------------------------------------------------------------
if __name__ == '__main__':
    try:
        # Get arguments.
        (action, uniqid) = get_args()

        # Create daemon object.
        DAEMON_NAME = DAEMON_NAME.replace('#ID#', uniqid)
        PIDFILE = PIDFILE.replace('#ID#', uniqid)
        RUNFILE = RUNFILE.replace('#ID#', uniqid)
        d = MyProc(name=DAEMON_NAME, pidfile=PIDFILE, runfile=RUNFILE,
                     stoptimeout=DAEMON_STOP_TIMEOUT, debug=DEBUG)

        # Action requested.
        if action == 'start':
            d.start()
        elif action == 'stop':
            d.stop()
        elif action == 'restart':
            d.restart()
        else:
            raise NameError('Unknown action')

        sys.exit(0)
    except Exception as err:
        if DEBUG:
            raise
        else:
            sys.stderr.write('%s\n' % err)

        sys.exit(1)
