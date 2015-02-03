#!/usr/bin/python3
#  -*- coding: utf-8 -*-
# File Copier
# Release Date:
#
# Author: Jayakrishnan Nair (https://github.com/jkvnair).
#
# Email: jnair93@gmail.com     Website: https://github.com/jkvnair/filecopy/
#
# "File Copy tool with pause button"

import sys
import os
import time
#import threading
from PyQt5.QtCore import pyqtSignal, QThread
from PyQt5.QtWidgets import (QApplication, QCheckBox, QDialog,
        QErrorMessage, QFileDialog, QFrame, QGridLayout,
        QLabel, QProgressBar, QPushButton)


class Dialog(QDialog):

    def __init__(self, parent=None):
        super(Dialog, self).__init__(parent)

        self.p = False
        self.startcopy = False
        self.q = False
        self.infile = 'in.bin'
        self.outfile = 'out.bin'
        self.closeonce = False
        self.delay = False
        self.k = 0

        self.openFilesPath = ''

        self.errorMessageDialog = QErrorMessage(self)

        frameStyle = QFrame.Sunken | QFrame.Panel

        #define widgets

        self.openFileNameLabel = QLabel()
        self.openFileNameLabel.setFrameStyle(frameStyle)
        self.openFileNameButton = QPushButton("Select Source file")

        self.saveFileNameLabel = QLabel()
        self.saveFileNameLabel.setFrameStyle(frameStyle)
        self.saveFileNameButton = QPushButton("Destination File")

        self.copybutton = QLabel()
        self.copybutton.setFrameStyle(frameStyle)
        self.copybutton = QPushButton("Copy")

        self.progressbar = QProgressBar()

        self.pausebutton = QLabel()
        self.pausebutton.setFrameStyle(frameStyle)
        self.pausebutton = QPushButton("Pause")

        self.quitbutton = QPushButton("Quit")

        self.speed = QLabel()
        self.speed.setFrameStyle(frameStyle)

        self.avgspeed = QLabel()
        self.avgspeed.setFrameStyle(frameStyle)

        self.remtime = QLabel()
        self.remtime.setFrameStyle(frameStyle)

        self.sizes = QLabel()
        self.sizes.setFrameStyle(frameStyle)

        self.version = QLabel()
        self.version.setFrameStyle(frameStyle)
        self.version.setText("pycopy v0.01 by Jay ")

        #connect signals

        self.openFileNameButton.clicked.connect(self.setOpenFileName)
        self.saveFileNameButton.clicked.connect(self.setSaveFileName)
        self.quitbutton.clicked.connect(self.closeEvent)
        self.copybutton.clicked.connect(self.copy)
        self.pausebutton.clicked.connect(self.pause)

        self.native = QCheckBox()
        self.native.setText("Use native file dialog.")
        self.native.setChecked(True)
        if sys.platform not in ("win32", "darwin"):
            self.native.hide()

        layout = QGridLayout()
        layout.setColumnStretch(1, 1)
        layout.setColumnMinimumWidth(1, 150)
        layout.addWidget(self.openFileNameButton, 0, 0)
        layout.addWidget(self.openFileNameLabel, 0, 1)
        layout.addWidget(self.saveFileNameButton, 1, 0)
        layout.addWidget(self.saveFileNameLabel, 1, 1)
        layout.addWidget(self.progressbar, 2, 0, 1, 2)
        layout.addWidget(self.speed, 3, 0)
        layout.addWidget(self.avgspeed, 3, 1)
        layout.addWidget(self.remtime, 4, 0)
        layout.addWidget(self.sizes, 4, 1,)
        layout.addWidget(self.pausebutton, 6, 0, 1, 2)
        layout.addWidget(self.quitbutton, 7, 1)
        layout.addWidget(self.copybutton, 7, 0)
        layout.addWidget(self.version, 8, 0, 1, 2)
        self.setLayout(layout)

        self.setWindowTitle("python copy with pause")

    def setOpenFileName(self):
        options = QFileDialog.Options()
        if not self.native.isChecked():
            options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self,
                "Select source", self.openFileNameLabel.text(),
                "All Files (*);;Text Files (*.txt)", options=options)
        if fileName:
            self.openFileNameLabel.setText(fileName)
            self.infile = fileName

    def setSaveFileName(self):
        options = QFileDialog.Options()
        if not self.native.isChecked():
            options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getSaveFileName(self,
                "Select destination",
                self.saveFileNameLabel.text(),
                "All Files (*);;Text Files (*.txt)", options=options)
        if fileName:
            self.saveFileNameLabel.setText(fileName)
            self.outfile = fileName

    def updateprogress(self, i):
        self.progressbar.setValue(int(i * 1024 / self.insize * 100.0 + 0.5))
        if (time.perf_counter() - self.prevtime) > 1.0:
            osize = os.path.getsize(self.outfile)
            curspeed = (osize - self.k)/ (time.perf_counter() - self.prevtime)
            avgspeed = osize/ (time.perf_counter()-self.starttime)
            dialog.speed.setText("cur: " + formatsize(curspeed) + "ps")
            dialog.avgspeed.setText("avg: " + formatsize(avgspeed) + "ps")
            self.prevtime = time.perf_counter()
            self.remtime.setText("Rem:" + formattime((self.insize - osize) / (osize/(time.perf_counter() - self.starttime)))+'s')
            self.sizes.setText("Rem:" + formatsize((self.insize - osize)))
            self.k = osize
            #if curspeed < 0.66 * avgspeed:
                #self.p = self.delay = True




    def pause(self):
        if not self.p:
            self.pausebutton.setText("Resume")
            self.p = True
        else:
            self.pausebutton.setText("Pause")
            self.p = False

    def copy(self):
        self.starttime = time.perf_counter()
        self.prevtime = self.starttime
        self.insize = os.path.getsize(self.infile)
        self.k = 0
        self.startcopy = True

    def closeEvent(self, QCloseEvent):

        self.p = False
        self.q = True
        if self.closeonce is False:
            self.close()
        self.closeonce = not self.closeonce


class Copier(QThread):
    progresssig = pyqtSignal(int)

    def __init__(self):
        super(Copier, self).__init__()
        #enthinanennariyilla threading.Thread.__init__(self)

    def run(self):
        print("copier started")

        while not dialog.q:
            if dialog.startcopy:
                self.copy()
                dialog.startcopy = False


    def copy(self):

            if dialog.infile is '\0':
                self.infile = 'in.bin'
            else:
                self.infile = dialog.infile
            if dialog.outfile is '\0':
                self.outfile = 'out.bin'
            else:
                self.outfile = dialog.outfile

            inf = open(self.infile, 'rb')
            outf = open(self.outfile, 'wb')

            inf.flush()
            outf.flush()

            self.i = 0

            while not dialog.q:
                buf = inf.read(1024)
                if len(buf) == 0:
                    break
                while dialog.p:
                    time.sleep(0.05)
                outf.write(buf)

                self.progresssig.emit(self.i)
                self.i += 1
            while os.path.getsize(self.outfile) != os.path.getsize(self.infile):
                self.progresssig.emit(self.i)
                print((os.path.getsize(self.outfile)),( os.path.getsize(self.infile)))
                time.sleep(1)
            #dialog.progress.setFormat("Done")
            inf.close()
            outf.close()

def formatsize(bits):

    bits = round(bits, 2)
    if bits < 1024:
        unit = ' b'
    elif bits < 1048576:
        unit = ' Kib'
        bits /= 1024
    elif bits < 1073741824:
        bits /= 1048576
        unit = ' Mib'
    else:
        bits /= 1073741824
        unit = ' Gib'

    #print("{:03.2f} {}".format( bps, unit ))
    return("%0.2f" % (bits + 0.005) + unit)

def formattime(time):
    time = round(time, 2)
    return str(time)

if __name__ == '__main__':
    app = QApplication(sys.argv)

    dialog = Dialog()

    copier = Copier()
    copier.start()

    copier.progresssig.connect(dialog.updateprogress)

    dialog.show()

    sys.exit(app.exec_())

