#!/usr/bin/env python3
# -*- coding:utf-8 -*-

###############################################################################
# dosya     : daemon.py
# ilgili    : emrah.com@gmail.com
#
# Daemon sinifini tanimlayan modul.
# Bu modul, servis (daemon) olarak calisacak betikler tarafindan import edilir.
# Modulu import eden betik, bu sinifi temel alarak kendi sinifini olusturur
# ve run metodu icine calisacak servis kodlarini koyar.
#
###############################################################################

import sys
import os
import time
import atexit
import signal
import inspect



# -----------------------------------------------------------------------------
# Temel daemon sinifi
# -----------------------------------------------------------------------------
class Daemon:
    def __init__(self, name, pidfile, runfile, stoptimeout=10, debug=0):
        # Daemon'in adi, mesajlarda kullanilacak.
        self.name = name

        # Daemon'in pid'sinin kaydedilecegi dosya.
        self.pidfile = pidfile

        # Daemon'i temiz kapatmak icin ic dongulerce varligi kontrol edilecek
        # dosya.
        self.runfile = runfile

        # Kill etmeden once daemon'in kendi kendini kapatmaya calismasina ne
        # kadar sure izin verecegimiz. Port, socket ve veritabani
        # islemlerindeki en buyuk timeout suresinden biraz uzun bir sure vermek
        # iyi olur.
        self.stoptimeout = stoptimeout

        # Debug yapiliyor mu? Debug yapiliyorsa ciktilar konsola, yapilmiyorsa
        # /dev/null'a yonlendirilecek.
        self.debug = debug

        # Daemon'in pathi.
        basedir = os.path.abspath(inspect.stack()[-1][1])
        basedir = os.path.dirname(basedir)
        self.basedir = basedir


    # -------------------------------------------------------------------------
    # UNIX double-fork magic
    # -------------------------------------------------------------------------
    def daemonize(self):
        # Birinci fork.
        # Bu sayede daemon, shellden calistirinca tekrar shell'e donulebilecek.
        try:
            pid = os.fork()
            if pid > 0:
                # Parenti sonlandir.
                sys.exit(0)
        except OSError as err:
            sys.stderr.write('fork #1 gerceklestirilemedi: %d (%s)\n' \
                            % (err.errno, err.stderror))
            sys.exit(1)

        # Parent baglantisini kopar.
        os.chdir('/')
        os.setsid()
        os.umask(0)

        # Ikinci fork.
        # Standart girdi ve ciktilari yonlendirmek icin yapiliyor.
        try:
            pid = os.fork()
            if pid > 0:
                # Parenti sonlandir.
                sys.exit(0)
        except OSError as err:
            sys.stderr.write('fork #2 gerceklestirilemedi: %d (%s)\n' \
                            % (err.errno, err.stderror))
            sys.exit(1)

        # Debug yapmiyorsak ciktilara ihtiyacimiz yok, /dev/null'a yonlendir.
        if not self.debug:
            # Standart dosya tanimlayicilarini yonlendir.
            sys.stdout.flush()
            sys.stderr.flush()
            sinp = open(os.devnull, 'rb')
            sout = open(os.devnull, 'ab+')
            serr = open(os.devnull, 'ab+', 0)
            os.dup2(sinp.fileno(), sys.stdin.fileno())
            os.dup2(sout.fileno(), sys.stdout.fileno())
            os.dup2(serr.fileno(), sys.stderr.fileno())

        # Daemon sonlandirilirken calisacak olan fonksiyonu set et.
        atexit.register(self.__delpid)

        # runfile dosyasini olustur.
        open(self.runfile, 'w+').write('1\n')

        # Pid'i pidfile dosyasina kaydet.
        pid = str(os.getpid())
        open(self.pidfile, 'w+').write('%s\n' % pid)


    # -------------------------------------------------------------------------
    # Daemon'i baslatan bolum.
    # -------------------------------------------------------------------------
    def start(self):
        # Daemon zaten calisiyor mu diye kontrol et.
        # Eger kayitli bir pid varsa calisiyordur.
        pid = self.__getpid()
        if pid:
            sys.stderr.write('%s zaten calisiyor\n' % self.name)
            sys.exit(1)

        # Daemoni baslat.
        sys.stdout.write('%s baslatiliyor...\n' % self.name)
        self.daemonize()
        self.run()


    # -------------------------------------------------------------------------
    # Daemon'i durduran bolum.
    # -------------------------------------------------------------------------
    def stop(self):
        # Oncelikle calisan bir daemon var mi diye kontrol et.
        # Eger kayitli bir pid yoksa zaten calismiyor demektir.
        pid = self.__getpid()
        if not pid:
            sys.stderr.write('%s zaten calismiyor\n' % self.name)
            sys.exit(1)

        # Daemon'i durdurma islemlerine basla.
        sys.stdout.write('%s durduruluyor' % self.name)

        # Oncelikle daemon'a kendisini kapatma sansi ver.
        # Kendi kendini kapatamazsa kill edilecek.
        self.__cleanstop(pid)

        # Daeman kill olana kadar belli araliklarla SIGTERM gonder.
        # Daemon kill olduktan sonraki kill denemesinde OSError olusacak.
        try:
            while True:
                os.kill(pid, signal.SIGTERM)
                time.sleep(0.1)
        except OSError as err:
            err = str(err)

            if err.find('No such process') > 0:
                if os.path.exists(self.pidfile):
                    os.remove(self.pidfile)
            else:
                sys.stderr.write('%s\n' % (err))
                sys.exit(1)


    # -------------------------------------------------------------------------
    # Daemoni yeniden baslatan bolum.
    # -------------------------------------------------------------------------
    def restart(self):
        self.stop()
        self.start()


    # -------------------------------------------------------------------------
    # runfile dosyasini silen bolum. Kendi kendini kapatacak olan daemon
    # uygulamalarinda, uygulama sonlanirken run dosyasini silmek icin
    # kullaniliyor.
    # -------------------------------------------------------------------------
    def delrun(self):
        try:
            os.remove(self.runfile)
        except Exception:
            pass


    # -------------------------------------------------------------------------
    # pidfile dosyasini silen bolum.
    # -------------------------------------------------------------------------
    def __delpid(self):
        try:
            os.remove(self.pidfile)
        except Exception:
            pass


    # -------------------------------------------------------------------------
    # Pid'i soyleyen bolum.
    # -------------------------------------------------------------------------
    def __getpid(self):
        # pidfile dosyasina kayitli bir pid var mi?
        try:
            pf = open(self.pidfile, 'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None

        return pid


    # -------------------------------------------------------------------------
    # Daemon'a kendini, kendi imkanlari ile kapatma sansi taniyan bolum.
    # -------------------------------------------------------------------------
    def __cleanstop(self, pid):
        # runfile siliniyor. Daemon icindeki donguler, bu dosyanin varligini
        # kontrol ediyor. Dosya yoksa dongulerden cikilacak ve daemon temiz bir
        # sekilde sonlanacak.
        try:
            os.remove(self.runfile)
        except Exception:
            pass

        # Daemon'in kapanmasini stoptimeout suresince bekle.
        t0 = time.time()
        result = False
        while True:
            sys.stdout.write('.')
            sys.stdout.flush()

            # Daemon'a sinyal 0 gonder.
            # OSError olusursa daemon kapanmis demektir.
            try:
                os.kill(pid, 0)
            except OSError:
                result = True
                break

            # stoptimeout suresi dolduysa daha fazla bekleme.
            if (time.time() - t0) > self.stoptimeout: break
            time.sleep(1)

        sys.stdout.write('\n')
        return result


    # -------------------------------------------------------------------------
    # run metodu
    # Alt sinif, bu metodu yeniden yazacak.
    # Daemon kodu, orada yer alacak.
    # -------------------------------------------------------------------------
    def run(self):
        pass
