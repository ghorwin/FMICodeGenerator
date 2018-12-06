import sys
import os
import platform
import PyQt5
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import QtGui, QtCore, QtWidgets
import os.path
from FMIGenerator import *

class GUI():
    
    def QWizardPage(self): 
        """ Develops Wizard pages to enter the required inputs for FMU Generation
        ModelName -- A user defined model name
        description -- A user defined description
        """
        
        
        self.labelModelName = QLabel('Model Name:')
        self.lineEditModelName = QLineEdit()
        self.labeldescription = QLabel('Description:')
        self.lineEditdescription = QTextEdit()
        self.labelTargetDir = QLabel('Target Location:')        
        self.lineEditTargetDir = QLineEdit()
        self.wizard = QWizard()        
        self.pushButtondestination = QToolButton()        
    
        
        # Different Wizard based on platform
        if platform.system() == 'Darwin':
            self.wizard.setWizardStyle(QWizard.MacStyle)
            
        elif platform.system() == 'Windows':
            self.wizard.setWizardStyle(QWizard.AeroStyle)
            
        else:
            self.wizard.setWizardStyle(QWizard.ModernStyle)
        
        # watermark,logo,banner and windowicon for wizard 
        self.wizard.setPixmap(QWizard.WatermarkPixmap,QPixmap('FMI.j'))
        self.wizard.setPixmap(QWizard.LogoPixmap,QPixmap('FMI.jpg'))
        self.wizard.setPixmap(QWizard.BannerPixmap,QPixmap('FMI.j'))
        self.wizard.setWindowIcon(QIcon('FMI.jpeg'))
        
        # setting up the first page of wizard with title and subtitile
        page1 = QWizardPage()
        page1.setTitle('FMU Initialization')
        page1.setSubTitle('Please enter the below details')
        
        # setting up the page 1 vertical BoxLayout
        vLayout1 = QVBoxLayout(page1)
        
        # adding required widgets for the page 1
        vLayout1.addWidget(self.labelModelName)
        vLayout1.addWidget(self.lineEditModelName)
        vLayout1.addWidget(self.labeldescription)
        vLayout1.addWidget(self.lineEditdescription)
        vLayout1.addWidget(self.labelTargetDir)
        
        # setting up page 1 horizontal BoxLayout
        hLayout1 = QHBoxLayout(page1)
        hLayout1.addWidget(self.lineEditTargetDir)
        hLayout1.addWidget(self.pushButtondestination)
        hLayout1.setStretch(0,1)
        self.pushButtondestination.setIcon(QtGui.QIcon('FMI.gif'))
        self.pushButtondestination.setIconSize(QtCore.QSize(24,18))        
        vLayout1.addLayout(hLayout1)
        
        
        # setting up the tool tips for page 1
        QToolTip.setFont(QFont('SansSerif', 10))
        self.lineEditModelName.setToolTip('Write new Model Name')
        self.lineEditdescription.setToolTip('Provide a new description') 
        self.pushButtondestination.setToolTip('Click to choose the directory') 
        
    
        # validating the entered ModelName
        self.validating(self.lineEditModelName)
        
        # setting up the pushButton for choosing the Target director location
        self.pushButtondestination.clicked.connect(self.selectFolder)
        
        # setting up page 2 of the wizard    
        page2 = QWizardPage()
        page2.setFinalPage(True)
        
        # setting the title and subtitle in page 2
        page2.setTitle('FMU Page 2')
        page2.setSubTitle('Fasih!')
        
        label1 = QLabel()
        
        # setting up the page 2 vertical BoxLayout
        vLayout2 = QVBoxLayout(page2)
        vLayout2.addWidget(label1)
        
        # parsing ModelName to page2 of wizard
        page1.registerField('Field1*',self.lineEditModelName,self.lineEditModelName.text(),self.lineEditModelName.textChanged)
        nxt = self.wizard.button(QWizard.NextButton)
        func1 = lambda:label1.setText(page1.field('Field1'))
        nxt.clicked.connect(func1)
        
        self.wizard.addPage(page1)
        self.wizard.addPage(page2)
        self.wizard.show()
        app.exec_()

               
    
    def validating(self,text):
        """ to validate the ModelName entered
        """
        regex = QtCore.QRegExp("[a-z-A-Z_äÄöÖüÜ§$%&()=#+;,0-9]+")
        validator = QRegExpValidator(regex)   
        text.setValidator(validator) 
    
    def selectFolder(self):
        """ to choose the valid directory path
        """
        filepath = QFileDialog.getExistingDirectory(None, "Select Directory")
        # check if user canceled the dialog, if it was canceled, string is empty and we do nothing
        if filepath == "":
            return

        # set new filepath in line edit
        self.lineEditTargetDir.setText(filepath)
                
              
if __name__ == '__main__':
        
    app = QApplication(sys.argv) 
    g = GUI()
    f = g.QWizardPage()
    

