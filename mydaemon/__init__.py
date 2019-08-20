#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import sys
import os
import time
import atexit
import signal
import inspect



# -----------------------------------------------------------------------------
# Daemon class
# -----------------------------------------------------------------------------
class Daemon:
    def __init__(self, name, pidfile, runfile, stoptimeout=10, debug=0):
        # Daemon name.
        self.name = name

        # Daemon pid file.
        self.pidfile = pidfile

        # Daemon run file. "stop" request deletes this file to inform the
        # process and waits [stoptimeout] seconds before to send SIGTERM.
        # The process has a change to stop cleanly if it's written
        # appropriately.
        self.runfile = runfile

        # Cleanstop wait time before to kill the process.
        self.stoptimeout = stoptimeout

        # The output goes to the standart output in debug mode, goes to
        # /dev/null in production mode.
        self.debug = debug

        # Daemon basedir.
        basedir = os.path.abspath(inspect.stack()[-1][1])
        basedir = os.path.dirname(basedir)
        self.basedir = basedir


    # -------------------------------------------------------------------------
    # UNIX double-fork magic
    # -------------------------------------------------------------------------
    def daemonize(self):
        # First fork.
        try:
            pid = os.fork()
            if pid > 0:
                # Stop the parent.
                sys.exit(0)
        except OSError as e:
            sys.stderr.write('fork #1 failed: %d (%s)\n' \
                            % (e.errno, e.stderror))
            sys.exit(1)

        # Decouple from parent.
        os.chdir('/')
        os.setsid()
        os.umask(0)

        # Second fork.
        try:
            pid = os.fork()
            if pid > 0:
                # Stop the parent.
                sys.exit(0)
        except OSError as e:
            sys.stderr.write('fork #2 failed: %d (%s)\n' \
                            % (e.errno, e.stderror))
            sys.exit(1)

        # Redirect the standart I/O to /dev/null in production mode.
        if not self.debug:
            sys.stdout.flush()
            sys.stderr.flush()
            sinp = open(os.devnull, 'rb')
            sout = open(os.devnull, 'ab+')
            serr = open(os.devnull, 'ab+', 0)
            os.dup2(sinp.fileno(), sys.stdin.fileno())
            os.dup2(sout.fileno(), sys.stdout.fileno())
            os.dup2(serr.fileno(), sys.stderr.fileno())

        # Register the function which run at exit.
        atexit.register(self.__delpid)

        # Create run file.
        open(self.runfile, 'w+').write('1\n')

        # Create pid file.
        pid = str(os.getpid())
        open(self.pidfile, 'w+').write('%s\n' % pid)


    # -------------------------------------------------------------------------
    # start
    # -------------------------------------------------------------------------
    def start(self):
        pid = self.__getpid()
        if pid:
            sys.stderr.write('%s is already running\n' % self.name)
            sys.exit(1)

        sys.stdout.write('%s is starting...\n' % self.name)
        self.daemonize()
        self.run()


    # -------------------------------------------------------------------------
    # stop
    # -------------------------------------------------------------------------
    def stop(self):
        pid = self.__getpid()
        if not pid:
            sys.stderr.write('%s is already stopped\n' % self.name)
            sys.exit(1)

        sys.stdout.write('%s is stopping' % self.name)

        # Wait for clean stop.
        self.__cleanstop(pid)

        # Send SIGTERM if the process continues to run.
        try:
            while True:
                os.kill(pid, signal.SIGTERM)
                time.sleep(0.1)
        except OSError as e:
            err = str(e)

            if err.find('No such process') > 0:
                if os.path.exists(self.pidfile):
                    os.remove(self.pidfile)
            else:
                sys.stderr.write('%s\n' % (e))
                sys.exit(1)


    # -------------------------------------------------------------------------
    # restart
    # -------------------------------------------------------------------------
    def restart(self):
        self.stop()
        self.start()


    # -------------------------------------------------------------------------
    # delete run file.
    # -------------------------------------------------------------------------
    def delrun(self):
        try:
            os.remove(self.runfile)
        except Exception:
            pass


    # -------------------------------------------------------------------------
    # delete pid file.
    # -------------------------------------------------------------------------
    def __delpid(self):
        try:
            os.remove(self.pidfile)
        except Exception:
            pass


    # -------------------------------------------------------------------------
    # get PID
    # -------------------------------------------------------------------------
    def __getpid(self):
        try:
            pf = open(self.pidfile, 'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None

        return pid


    # -------------------------------------------------------------------------
    # Clean stop
    # -------------------------------------------------------------------------
    def __cleanstop(self, pid):
        # remove run file to inform the process for stop request.
        try:
            os.remove(self.runfile)
        except Exception:
            pass

        # Wait [stoptimeout] seconds.
        t0 = time.time()
        result = False
        while True:
            sys.stdout.write('.')
            sys.stdout.flush()

            # Check the process.
            try:
                os.kill(pid, 0)
            except OSError:
                result = True
                break

            # Stop waiting if [stoptimeout] seconds pass.
            if (time.time() - t0) > self.stoptimeout: break
            time.sleep(1)

        sys.stdout.write('\n')
        return result


    # -------------------------------------------------------------------------
    # run
    # -------------------------------------------------------------------------
    def run(self):
        pass
