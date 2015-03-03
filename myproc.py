#!/usr/bin/python3
# -*- coding:utf-8 -*-

###############################################################################
# dosya     : myproc.py
# ilgili    : emrah.com@gmail.com
#
# daemon.py modulunu kullanan ornek background process. "stop" komutu
# verilmeden isi biterse kendini duzgun bir sekilde kapatir. Farkli "uniqid"
# degerleri verilerek istenildigi kadar process baslatilabilir.
#
# Kullanimi:
#       myproc.py start|stop|restart uniqid
#
###############################################################################

import os
import sys
import time
import atexit
import argparse
from   daemon import Daemon

# Daemon mesajlarinda kullanilacak olan daemon adi.
DAEMON_NAME = 'My Background Process (id: #ID#)'
# Daemon'a cleanstop icin ne kadar sure taninacagi. Bu sure icinde kendini
# kapamazsa kill edilir.
DAEMON_STOP_TIMEOUT = 10
# Daemon'in Pid numarasini tutan dosya.
PIDFILE = '/tmp/myproc_#ID#.pid'
# Dongulerin devam edip etmeyeceklerini belirleyen dosya.
RUNFILE = '/tmp/myproc_#ID#.run'
# Debug yapilacak mi? Test ortami icin 1, gercek calisma ortami icin 0
# Default olarak bu deger, config.py dosyasindan geliyor.
DEBUG = 0



# -----------------------------------------------------------------------------
def get_args():
    '''
    Argumanlari alir, kontrol eder ve bir liste seklinde dondurur.

    >>> get_args()
    ('start', 5)
    >>> get_args()
    ('stop', 4)
    '''

    try:
        parser =  argparse.ArgumentParser()
        parser.add_argument('action', help='İşlem komutu',
                            choices=['start', 'stop', 'restart'])
        parser.add_argument('uniqid', help='İşlem kodu')
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
        MyProc sinifi, run metodu. Bu siniftan turetilen nesneye 'start'
        komutu verildiginde, bu bolum calisir.
        '''

        # Daemon'a kapanma emri gelmeden islem tamamlanirsa run dosyasini
        # cikista kendi temizleyecek.
        atexit.register(self.delrun)

        # Daemona kapanma emri verilirse dongu sona erecek. Kapanma emri
        # verilip verilmedigini RUNFILE'in varligindan anliyoruz. Dosya varsa
        # islem bitene kadar calismaya devam eder.
        n = 0
        while os.path.exists(RUNFILE):
            print('.')
            n += 1

            if (n > 60):
                break

            time.sleep(1)



# -----------------------------------------------------------------------------
# Program ana bolum. Program, bu bolumden calismaya baslar.
# -----------------------------------------------------------------------------
if __name__ == '__main__':
    try:
        # Argumanlari al.
        (action, uniqid) = get_args()

        # Daemon nesnesini olustur.
        DAEMON_NAME = DAEMON_NAME.replace('#ID#', uniqid)
        PIDFILE = PIDFILE.replace('#ID#', uniqid)
        RUNFILE = RUNFILE.replace('#ID#', uniqid)
        d = MyProc(name=DAEMON_NAME, pidfile=PIDFILE, runfile=RUNFILE,
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
