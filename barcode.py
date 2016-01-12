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
from PyQt4 import QtGui

class gui(QtGui.QWidget):
  width = 500
  height = 400
  
  def __init__(self):
    super(gui, self).__init__()
    self.initUI()
  
  def initUI(self):
    # Set window size. 
    self.resize(self.width, self.height)
     
    # Set window title  
    self.setWindowTitle("Barcode")
    self.doLayout();
    
    self.center()
    self.show() 
    
  def center(self):
    frameGm = self.frameGeometry()
    screen = QtGui.QApplication.desktop().screenNumber(QtGui.QApplication.desktop().cursor().pos())
    centerPoint = QtGui.QApplication.desktop().screenGeometry(screen).center()
    frameGm.moveCenter(centerPoint)
    self.move(frameGm.topLeft())
    
  def doLayout(self):
    vbox	 = QtGui.QVBoxLayout()

    hbox1	 = QtGui.QHBoxLayout()
    btnSrc = QtGui.QPushButton('Source Dir')
    btnSrc.clicked.connect(lambda: self.chooseDir('src'))
    btnSrc.setMaximumWidth(140)
    hbox1.addWidget(btnSrc, 2)
    self.labelSrc = QtGui.QLabel("")
    #labelSrc.setFixedWidth(200)
    self.labelSrc.setWordWrap(True)
    hbox1.addWidget(self.labelSrc, 4)
    vbox.addLayout(hbox1)
    
    hbox2	 = QtGui.QHBoxLayout()
    btnDst = QtGui.QPushButton('Destination Dir')
    btnDst.clicked.connect(lambda: self.chooseDir('dst'))
    btnDst.setMaximumWidth(140)
    hbox2.addWidget(btnDst, 2)
    self.labelDst = QtGui.QLabel("")
    #labelDst.setFixedWidth(200)
    self.labelDst.setWordWrap(True)
    hbox2.addWidget(self.labelDst, 4)
    vbox.addLayout(hbox2)
    
    hbox3	 = QtGui.QHBoxLayout()
    self.inputMove = QtGui.QCheckBox('Move files', self)
    self.inputMove.toggle()
    hbox3.addWidget(self.inputMove)
    vbox.addLayout(hbox3)
    
    hbox4	 = QtGui.QHBoxLayout()
    self.logOutput = QtGui.QTextEdit()
    self.logOutput.setReadOnly(True)
    self.logOutput.setLineWrapMode(QtGui.QTextEdit.NoWrap)
    self.logOutput.moveCursor(QtGui.QTextCursor.End)
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
    btnS = QtGui.QPushButton('Start')
    btnS.clicked.connect(self.parseImg)
    btnS.setMaximumWidth(140)
    hboxBottom.addWidget(btnS)
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
    
    extractor = extract(dirSrc, dirDst)
    extractor.process(self.inputMove.isChecked()) 
    
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
    # create a reader
    scanner = zbar.ImageScanner()
    
    # configure the reader
    scanner.parse_config('enable')
    
    # obtain image data
    pil = Image.open(img).convert('L')
    width, height = pil.size
    raw = pil.tostring()
    
    # wrap image data
    image = zbar.Image(width, height, 'Y800', raw)
    
    # scan the image for barcodes
    scanner.scan(image)
    
    # extract results
    code = None
    for symbol in image:
      log('decoded '+str(symbol.type)+' symbol "'+str(symbol.data)+'"')
      code = symbol.data
      #break
  
    # clean up
    del(image)
    return code

def log(msg):
  print msg
  try:
    global interface
    interface.logOutput.insertPlainText(msg+"\n")
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
  interface = gui()
  sys.exit(a.exec_())
  