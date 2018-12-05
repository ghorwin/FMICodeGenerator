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
    
    def __init__(self):
        
        
        self.labelModelName = QLabel('Model Name:')
        self.description = QLabel('Description:')          
        self.lineEditModelName = QLineEdit()
        self.descriptionEdit = QTextEdit()  
        self.wizard = QWizard()
        self.TargetDir = QLabel('Target Location:')
        self.TargetDirEdit = ""
        
        self.destinationButton = QPushButton()
    
    def QWizardPage(self): 
        
        
        
        if platform.system() == 'Darwin':
            self.wizard.setWizardStyle(QWizard.MacStyle)
            
        elif platform.system() == 'Windows':
            self.wizard.setWizardStyle(QWizard.AeroStyle)
            
        else:
            self.wizard.setWizardStyle(QWizard.ModernStyle)
        
        
        self.wizard.setPixmap(QWizard.WatermarkPixmap,QPixmap('FMI.j'))
        self.wizard.setPixmap(QWizard.LogoPixmap,QPixmap('FMI.jpg'))
        self.wizard.setPixmap(QWizard.BannerPixmap,QPixmap('FMI.j'))
        self.wizard.setWindowIcon(QIcon('FMI.jpeg'))
        
        page1 = QWizardPage()
        page1.setTitle('FMU Initialization')
        page1.setSubTitle('Please enter the below details')
        

        vLayout1 = QVBoxLayout(page1)
        vLayout1.addWidget(self.modelName)
        vLayout1.addWidget(self.modelNameEdit)
        vLayout1.addWidget(self.description)
        vLayout1.addWidget(self.descriptionEdit)
        
        
        hLayout1 = QHBoxLayout(page1)
        hLayout1.addWidget(self.TargetDir)
        hLayout1.addWidget(self.destinationButton)
        hLayout1.setStretch(0,1)
        
        vLayout1.addLayout(hLayout1)
        
        
        
        QToolTip.setFont(QFont('SansSerif', 10))
        self.modelNameEdit.setToolTip('Write new Model Name')
        self.descriptionEdit.setToolTip('Provide a new description')          
        
        page1.registerField('Field1*',self.modelNameEdit,self.modelNameEdit.text(),self.modelNameEdit.textChanged)
        
        self.destinationButton.clicked.connect(self.selectFile)
        self.TargetDirEdit = QLineEdit(str(self.TargetDir) + '/' + str(self.modelNameEdit))
        vLayout1.addWidget(self.TargetDirEdit)
                                       
        
        
     
        

        page2 = QWizardPage()
        page2.setFinalPage(True)
        
        page2.setTitle('FMU Page 2')
        page2.setSubTitle('Fasih!')
        
        label1 = QLabel()
        
        vLayout2 = QVBoxLayout(page2)
        vLayout2.addWidget(label1)
        
        
        nxt = self.wizard.button(QWizard.NextButton)
        func1 = lambda:label1.setText(page1.field('Field1'))
        self.validating(self.modelNameEdit)
    
        nxt.clicked.connect(func1)
       
        
               
        
        
        
        
        self.wizard.addPage(page1)
        self.wizard.addPage(page2)
        
        self.wizard.show()
        app.exec_()

               
    
    def validating(self,text):
              
        regex = QtCore.QRegExp("[a-z-A-Z_äÄöÖüÜ§$%&()=#+;,0-9]+")
        validator = QRegExpValidator(regex)   
        text.setValidator(validator) 
    
    def selectFile(self):
        filepath = QFileDialog.getExistingDirectory(None, "Select Directory")

        
              
if __name__ == '__main__':
        
    app = QApplication(sys.argv) 
    g = GUI()
    f = g.QWizardPage()
    

