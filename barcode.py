#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
import os
import sys
import shutil
import argparse
import zbar
#import Image
from PIL import Image
from PIL import ImageEnhance
from PyQt4 import QtGui
from PyQt4.QtCore import Qt

#import thread;

class gui(QtGui.QWidget):
  width = 500
  height = 400
  
  def __init__(self, args):
    super(gui, self).__init__()
    self.initUI(args)
    
  def initUI(self, args):
    # Set window size. 
    self.resize(self.width, self.height)
     
    # Set window title  
    self.setWindowTitle("Barcode")
    self.doLayout(args);
    
    self.center()
    self.show() 
    
  def center(self):
    frameGm = self.frameGeometry()
    screen = QtGui.QApplication.desktop().screenNumber(QtGui.QApplication.desktop().cursor().pos())
    centerPoint = QtGui.QApplication.desktop().screenGeometry(screen).center()
    frameGm.moveCenter(centerPoint)
    self.move(frameGm.topLeft())
    
  def doLayout(self, args):
    vbox	 = QtGui.QVBoxLayout()

    hbox1	 = QtGui.QHBoxLayout()
    btnSrc = QtGui.QPushButton('Source Dir')
    btnSrc.clicked.connect(lambda: self.chooseDir('src'))
    btnSrc.setMaximumWidth(140)
    hbox1.addWidget(btnSrc, 2)
    self.labelSrc = QtGui.QLabel(args.src)
    #labelSrc.setFixedWidth(200)
    self.labelSrc.setWordWrap(True)
    hbox1.addWidget(self.labelSrc, 4)
    vbox.addLayout(hbox1)
    
    hbox2	 = QtGui.QHBoxLayout()
    btnDst = QtGui.QPushButton('Destination Dir')
    btnDst.clicked.connect(lambda: self.chooseDir('dst'))
    btnDst.setMaximumWidth(140)
    hbox2.addWidget(btnDst, 2)
    self.labelDst = QtGui.QLabel(args.dst)
    #labelDst.setFixedWidth(200)
    self.labelDst.setWordWrap(True)
    hbox2.addWidget(self.labelDst, 4)
    vbox.addLayout(hbox2)
    
    hbox3	 = QtGui.QHBoxLayout()
    self.inputMove = QtGui.QCheckBox('Move files', self)
    if(args.move):
      self.inputMove.toggle()
    hbox3.addWidget(self.inputMove)
    vbox.addLayout(hbox3)
    
    hbox4	 = QtGui.QHBoxLayout()
    self.logOutput = QtGui.QTextEdit()
    self.logOutput.setReadOnly(True)
    self.logOutput.setLineWrapMode(QtGui.QTextEdit.NoWrap)
    #self.logOutput.moveCursor(QtGui.QTextCursor.End)
    font = self.logOutput.font()
    font.setFamily("Courier")
    font.setPointSize(10)
    self.logOutput.setCurrentFont(font)
    self.logOutput.setTextColor(QtGui.QColor("darkCyan"))
    #self.logOutput.setTextBackgroundColor(QColor("gray"))
    #self.logOutput.insertPlainText(text)
    sb = self.logOutput.verticalScrollBar()
    sb.setValue(sb.maximum())
    hbox4.addWidget(self.logOutput)
    vbox.addLayout(hbox4)
    
    hboxBottom	 = QtGui.QHBoxLayout()
    self.btnS = QtGui.QPushButton('Start')
    self.btnS.clicked.connect(self.parseImg)
    self.btnS.setMaximumWidth(140)
    hboxBottom.addWidget(self.btnS)
    btnQ = QtGui.QPushButton('Exit')
    btnQ.clicked.connect(exit)
    btnQ.setMaximumWidth(140)
    hboxBottom.addWidget(btnQ)
    vbox.addLayout(hboxBottom)
     
    self.setLayout(vbox)      
  
  def chooseDir(self, dirType):
    #filename = QFileDialog.getOpenFileName(w, 'Open File', '/')
    selDir = str(QtGui.QFileDialog.getExistingDirectory(self, "Select Directory", "~"))
    if(dirType=='src'):
      self.labelSrc.setText(selDir)
    else :
      self.labelDst.setText(selDir)

  def parseImg(self):
    dirSrc = str(self.labelSrc.text());
    dirDst = str(self.labelDst.text());
    
    if((len(dirSrc) == 0) or (len(dirDst) == 0)):
      QtGui.QMessageBox.information(self,
                                    "Error",
                                    "Please specify a source and a destination directory")
      return False
    if(dirSrc == dirDst):
      QtGui.QMessageBox.information(self,
                                    "Error",
                                    "Source and Destination can not be the same")
      return False
    
    interface.logOutput.setPlainText("")
    #self.btnS.setEnabled(False);
    QtGui.QApplication.setOverrideCursor(QtGui.QCursor(Qt.WaitCursor))
    
    extractor = extract(dirSrc, dirDst)
    extractor.process(self.inputMove.isChecked())
    
    QtGui.QApplication.restoreOverrideCursor()
    #self.btnS.setEnabled(True);
    
    #thread.start_new_thread(extractor.process, (self.inputMove.isChecked()))
    
    return True
    
class extract():
  total = 0
  renamed = 0
  skipped = 0
  
  def __init__(self, dirSrc, dirDst):
    self.dirSrc = dirSrc
    self.dirDst = dirDst
    
  def process(self, move):
    #create dst directory if it does not exist
    if not os.path.exists(self.dirDst):
      os.makedirs(self.dirDst)
    
    for root, dirs, filenames in os.walk(self.dirSrc):
      log('PARSE FILES ...')
      log('--------------------------')
      for f in filenames:
        self.total = self.total+1
        log(f)
        code = self.scan(os.path.join(self.dirSrc, f))
        if (code != None) :
          self.renamed = self.renamed+1
          extension = os.path.splitext(f)[1]
          if move:
            shutil.move(os.path.join(self.dirSrc, f), os.path.join(self.dirDst, (code + extension)))
          else:
            shutil.copyfile(os.path.join(self.dirSrc,f), os.path.join(self.dirDst, (code + extension)))
        else:
          self.skipped = self.skipped+1
          log('BAR CODE NOT FOUND !!!')
        log('--------------------------')
    log('total = '+str(self.total)+' renamed = '+str(self.renamed)+' skipped = '+str(self.skipped))

  def scan(self, img):
    pilImage = Image.open(img).convert('L');
    
    code = None
    code = self.detectBarcode(pilImage)
    
    #try enchance
    if(code == None) :
      for i in range(9):
        enhancerB = ImageEnhance.Brightness(pilImage)
        factorB = 1.0+float(i)/10
        pilImage = enhancerB.enhance(factorB)
        
        for j in range(9):
          enhancerC = ImageEnhance.Contrast(pilImage)
          factorC = 1.0+float(j)/10
          pilImage = enhancerC.enhance(factorC)
          code = self.detectBarcode(pilImage)
          if(code != None):
            #log('enchance '+str(factorB))
            #log('enchance '+str(factorC))
            #pilImage.save('/home/cip/dst/test.jpg')
            break
        if(code != None):
          break
  
    # clean up
    del(pilImage)
    return code
  
  def detectBarcode(self, pilImage) :
    width, height = pilImage.size
    raw = pilImage.tostring()
    
    # create a reader
    scanner = zbar.ImageScanner()
    # configure the reader
    scanner.parse_config('enable')
    
    # wrap image data
    image = zbar.Image(width, height, 'Y800', raw)
    
    # scan the image for barcodes
    scanner.scan(image)
    
    # extract results
    code = None
    for symbol in image:
      log('decoded '+str(symbol.type)+' symbol "'+str(symbol.data)+'"')
      code = symbol.data
      break
    
    del(image)
    return code

def log(msg):
  print msg
  try:
    global interface
    interface.logOutput.insertPlainText(msg+"\n")
    interface.logOutput.moveCursor(QtGui.QTextCursor.End)
  except:
    pass
    
############################################################################################
parser = argparse.ArgumentParser()
parser.add_argument("-g", "--gui", help="enable GUI", action="store_true")
parser.add_argument("-m", "--move", help="delete files from source directory after rename", action="store_true")
parser.add_argument("-s", "--src", help="source directory")
parser.add_argument("-d", "--dst", help="destination directory")
args = parser.parse_args()

if(not args.gui):
  extractor = extract(args.src, args.dst)
  extractor.process(args.move)
else:
  # Create an PyQT4 application object.
  a = QtGui.QApplication(sys.argv)
  interface = gui(args)
  sys.exit(a.exec_())
  