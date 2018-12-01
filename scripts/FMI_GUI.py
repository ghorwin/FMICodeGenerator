import sys
import platform
import PyQt5
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import QtGui, QtCore

class GUI():
    
    def __init__(self):
        
        
        self.modelName = QLabel('Model Name:')
        self.description = QLabel('Description:')          
        self.modelNameEdit = QLineEdit()
        self.descriptionEdit = QTextEdit()  
        self.wizard = QWizard()
        
    
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
        
        QToolTip.setFont(QFont('SansSerif', 10))
        self.modelNameEdit.setToolTip('Write new Model Name')
        self.descriptionEdit.setToolTip('Provide a new description')          
        
        page1.registerField('Field1*',self.modelNameEdit,self.modelNameEdit.text(),self.modelNameEdit.textChanged)
       
       
       
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
     
              
if __name__ == '__main__':
        
    app = QApplication(sys.argv) 
    g = GUI()
    f = g.QWizardPage()
    

