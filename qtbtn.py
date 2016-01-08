#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
import sys
from PyQt4.QtGui import *
 
 
def chooseDir(dirType):
  #filename = QFileDialog.getOpenFileName(w, 'Open File', '/')
  selDir = str(QFileDialog.getExistingDirectory(w, "Select Directory"))
  if(dirType=='src'):
    labelSrc.setText(selDir)
  else :
    labelDst.setText(selDir)
  print selDir

def parseImg():
  print "parseImg"
  
############################################################################################ 
 
# Create an PyQT4 application object.
a = QApplication(sys.argv)       
 
# The QWidget widget is the base class of all user interface objects in PyQt4.
w = QWidget()
 
# Set window size. 
w.resize(500, 400)
 
# Set window title  
w.setWindowTitle("Barcode") 
 
vbox	 = QVBoxLayout()

hbox1	 = QHBoxLayout()
btnSrc = QPushButton('Source Dir')
btnSrc.clicked.connect(lambda: chooseDir('src'))
btnSrc.setMaximumWidth(140)
hbox1.addWidget(btnSrc, 2)
labelSrc = QLabel("")
#labelSrc.setFixedWidth(200)
labelSrc.setWordWrap(True)
hbox1.addWidget(labelSrc, 4)
vbox.addLayout(hbox1)

hbox2	 = QHBoxLayout()
btnDst = QPushButton('Destination Dir')
btnDst.clicked.connect(lambda: chooseDir('dst'))
btnDst.setMaximumWidth(140)
hbox2.addWidget(btnDst, 2)
labelDst = QLabel("")
#labelDst.setFixedWidth(200)
labelDst.setWordWrap(True)
hbox2.addWidget(labelDst, 4)
vbox.addLayout(hbox2)

text = "sssss"
#color = green;

hbox3	 = QHBoxLayout()
logOutput = QTextEdit()
logOutput.setReadOnly(True)
logOutput.setLineWrapMode(QTextEdit.NoWrap)
logOutput.moveCursor(QTextCursor.End)
font = logOutput.font()
font.setFamily("Courier")
font.setPointSize(10)
logOutput.setCurrentFont(font)
logOutput.setTextColor(QColor("darkCyan"))
#logOutput.setTextBackgroundColor(QColor("gray"))
logOutput.insertPlainText(text)
sb = logOutput.verticalScrollBar()
sb.setValue(sb.maximum())
hbox3.addWidget(logOutput)
vbox.addLayout(hbox3)

hboxBottom	 = QHBoxLayout()
btnS = QPushButton('Start')
btnS.clicked.connect(parseImg)
hboxBottom.addWidget(btnS)
btnQ = QPushButton('Exit')
btnQ.clicked.connect(exit)
hboxBottom.addWidget(btnQ)
vbox.addLayout(hboxBottom)


 
w.setLayout(vbox)      
w.show() 
 
sys.exit(a.exec_())