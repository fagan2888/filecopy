#!/usr/bin/python
import sys,os,time,threading
from PyQt5.QtCore import QDir, Qt
from PyQt5.QtWidgets import (QApplication, QCheckBox, QDialog,
        QErrorMessage, QFileDialog, QFontDialog, QFrame, QGridLayout,
        QInputDialog, QLabel, QProgressBar, QMessageBox, QPushButton)


class Dialog(QDialog):
       
    def __init__(self, parent=None):
        super(Dialog, self).__init__(parent)

        self.p = False
        self.startcopy = False
        self.q = False


        self.openFilesPath = ''

        self.errorMessageDialog = QErrorMessage(self)

        frameStyle = QFrame.Sunken | QFrame.Panel

        self.openFileNameLabel = QLabel()
        self.openFileNameLabel.setFrameStyle(frameStyle)
        self.openFileNameButton = QPushButton("Select Source file")

        self.saveFileNameLabel = QLabel()
        self.saveFileNameLabel.setFrameStyle(frameStyle)
        self.saveFileNameButton = QPushButton("Destination File")
        
        self.copybutton = QLabel()
        self.copybutton.setFrameStyle(frameStyle)
        self.copybutton = QPushButton("Copy")
        
        self.progress = QProgressBar()
        
        self.pausebutton = QLabel()
        self.pausebutton.setFrameStyle(frameStyle)
        self.pausebutton = QPushButton("Pause")

        
        self.quitbutton = QPushButton("Quit")
        
        self.speed = QLabel()
        self.speed.setFrameStyle(frameStyle)
        
        self.avgspeed = QLabel()
        self.avgspeed.setFrameStyle(frameStyle)

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
        layout.addWidget(self.progress, 2, 0, 1, 2)
        layout.addWidget(self.speed, 3, 0,)
        layout.addWidget(self.avgspeed, 3, 1,)
        layout.addWidget(self.pausebutton, 4, 0, 1, 2)
        layout.addWidget(self.quitbutton, 5, 1)
        layout.addWidget(self.copybutton, 5, 0)
        self.setLayout(layout)

        self.setWindowTitle("python copy with pause")
        

   
    def setOpenFileName(self):    
        options = QFileDialog.Options()
        if not self.native.isChecked():
            options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self,
                "QFileDialog.getOpenFileName()", self.openFileNameLabel.text(),
                "All Files (*);;Text Files (*.txt)", options=options)
        if fileName:
            self.openFileNameLabel.setText(fileName)
            self.inputfile = fileName
    
    def setSaveFileName(self):    
        options = QFileDialog.Options()
        if not self.native.isChecked():
            options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getSaveFileName(self,
                "QFileDialog.getSaveFileName()",
                self.saveFileNameLabel.text(),
                "All Files (*);;Text Files (*.txt)", options=options)
        if fileName:
            self.saveFileNameLabel.setText(fileName)
            self.outputfile = fileName
    
    def pause(self):
       if not self.p:
          self.pausebutton.setText("Resume")
          self.p = True
       else:
          self.pausebutton.setText("Pause")
          self.p = False
      
   
       
    def copy(self):
        self.startcopy = True
        starttime = time.perf_counter()
            
            
    def closeEvent(self, QCloseEvent ):
        print("closeevent1")
        self.p = False
        self.q = True
        self.close()
              
class Copier(threading.Thread):
    def __init__(self):
        super(Copier, self).__init__()
        #enthinanennariyilla threading.Thread.__init__(self)
        
    def run(self):
        print("copier started")

        while not dialog.q:
            if dialog.startcopy == True:
                self.copy()
                dialog.startcopy = False
            
    
    def copy(self):
            self.inputfile = 'in.bin'
            self.outputfile = 'out.bin'

            inf = open(self.inputfile,'rb')
            outf = open(self.outputfile,'wb')
       
            inf.flush()
            outf.flush()
       
            dialog.progress.setValue(0)
            insize = os.path.getsize(self.inputfile)
            starttime = time.perf_counter()
            prevtime = time.perf_counter() 
            self.i = 0
       
            while dialog.q == False:
                buf = inf.read(1024)
                if len(buf) == 0:
                    print ("done") 
                    break
                while True:
                    if dialog.p == False:
                        break
                    time.sleep(0.05)
                outf.write(buf)
             
                if (time.perf_counter()-prevtime)>1.0:
                    dialog.speed.setText("current: "+formatspeed(copier.i*1024/(time.perf_counter()-prevtime)))
                    dialog.avgspeed.setText("avg: "+formatspeed(copier.i*1024/(time.perf_counter()-starttime)))
                    prevtime = time.perf_counter()

                dialog.progress.setValue(int(self.i*1024/insize * 100.0+0.5))
                self.i+=1

            dialog.progress.setFormat("Done")
            inf.close()
            outf.close()
def formatspeed(bps):
   
    if bps < 1024:
        unit = ' bps'
    elif bps < 1048576:
        unit = ' Kibps'
        bps /= 1024
    #elif bps < 1073741824:
    else:
        
        bps /= 1048576
        unit = ' Mibps'
    #print("{:03.2f} {}".format( bps, unit ))   
    return( str(bps)[:7] + unit) 
    

if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    dialog = Dialog()
    
    copier = Copier()
    copier.start()
    
    print('here')
    dialog.show()
    sys.exit(app.exec_())
    
