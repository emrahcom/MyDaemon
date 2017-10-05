#!/usr/bin/python3
# -*- coding:utf-8 -*-

###############################################################################
# dosya     : mydaemon.py
# ilgili    : emrah.com@gmail.com
#
# daemon.py modulunu kullanan ornek servis.
#
# Kullanimi:
#       mydaemon.py start|stop|restart
#
###############################################################################

import os
import sys
import time
import argparse
from   daemon import Daemon

# Daemon mesajlarinda kullanilacak olan daemon adi.
DAEMON_NAME = 'My Daemon'
# Daemon'a cleanstop icin ne kadar sure taninacagi. Bu sure icinde kendini
# kapamazsa kill edilir.
DAEMON_STOP_TIMEOUT = 10
# Daemon'in Pid numarasini tutan dosya.
PIDFILE = '/tmp/mydaemon.pid'
# Dongulerin devam edip etmeyeceklerini belirleyen dosya.
RUNFILE = '/tmp/mydaemon.run'
# Dongunun her turundan sonra ne kadar sure beklenilecegi (saniye).
LOOP_SLEEP = 2
# Debug yapilacak mi? Test ortami icin 1, gercek calisma ortami icin 0
# Default olarak bu deger, config.py dosyasindan geliyor.
DEBUG = 0



# -----------------------------------------------------------------------------
def get_args():
    '''
    Argumanlari alir, kontrol eder ve bir liste seklinde dondurur.

    >>> get_args()
    ('start',)
    >>> get_args()
    ('stop',)
    '''

    try:
        parser =  argparse.ArgumentParser()
        parser.add_argument('action', help='İşlem komutu',
                            choices=['start', 'stop', 'restart'])
        args = parser.parse_args()

        result = (args.action, )
    except Exception as err:
        if DEBUG:
            raise
        else:
            sys.stderr.write('%s\n' % (err))

        result = (None, )

    return result



# -----------------------------------------------------------------------------
def wait(timeout=60):
    '''
    Timeout suresince bekletir. Bekleme esnasinda daemon'a kapanma emri gelirse
    bekleme yapmadan cikar.

    >>> wait(20)
    True
    >>> wait(None)
    False
    '''
    try:
        # Deamona kapanma emri gelmedigi surece timeout suresi kadar beklemede
        # kal.
        t0 = time.time()
        while os.path.exists(RUNFILE) and ((time.time()-t0) < timeout):
            time.sleep(1.0)

        result = True
    except Exception as err:
        if DEBUG:
            raise
        else:
            sys.stderr.write('%s\n' % (err))

        result = False

    return result



# -----------------------------------------------------------------------------
class MyDaemon(Daemon):
    def run(self):
        '''
        MyDaemon sinifi, run metodu. Bu siniftan turetilen nesneye 'start'
        komutu verildiginde, bu bolum calisir.
        '''

        # Daemona kapanma emri verilirse dongu sona erecek. Kapanma emri
        # verilip verilmedigini RUNFILE'in varligindan anliyoruz. Dosya varsa
        # calismaya devam et.
        while os.path.exists(RUNFILE):
            try:
                # Daemon calisirken buradaki islemleri surekli tekrarlar.
                pass
                pass
                pass
            except Exception as err:
                if DEBUG:
                    raise
                else:
                    sys.stderr.write('%s\n' % (err))
            finally:
                # Donguyu yeniden baslatmadan once bir sure bekle.
                wait(timeout=LOOP_SLEEP)



# -----------------------------------------------------------------------------
# Program ana bolum. Program, bu bolumden calismaya baslar.
# -----------------------------------------------------------------------------
if __name__ == '__main__':
    try:
        # Argumanlari al.
        (action, ) = get_args()

        # Daemon nesnesini olustur.
        d = MyDaemon(name=DAEMON_NAME, pidfile=PIDFILE, runfile=RUNFILE,
                     stoptimeout=DAEMON_STOP_TIMEOUT, debug=DEBUG)

        # Islem tipine gore gereken metodu cagir.
        if action == 'start':
            d.start()
        elif action == 'stop':
            d.stop()
        elif action == 'restart':
            d.restart()
        else:
            raise NameError('Bilinmeyen islem tipi')

        sys.exit(0)
    except Exception as err:
        if DEBUG:
            raise
        else:
            sys.stderr.write('%s\n' % err)

        sys.exit(1)
