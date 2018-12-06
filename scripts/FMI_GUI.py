import sys
import os
import platform
import PyQt5
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import QtGui, QtCore, QtWidgets
import os.path
from PyQt5 import uic
from FMIGenerator import *

class GUI():
    
    def __init__(self):
        
        self.labelModelName = QLabel('Model Name:')
        self.lineEditModelName = QLineEdit()
        self.labeldescription = QLabel('Description:')
        self.lineEditdescription = QTextEdit()
        self.labelTargetDir = QLabel('Target Location:')        
        self.lineEditTargetDir = QLineEdit()
        self.wizard = QWizard()        
        self.pushButtondestination = QToolButton()        
        self.pushbuttonClearContentClicked = QPushButton()  
        
    def QWizardPage(self): 
        """ Develops Wizard pages to enter the required inputs for FMU Generation
        ModelName -- A user defined model name
        description -- A user defined description
        """
    
        # Different Wizard based on platform
        if platform.system() == 'Darwin':
            self.wizard.setWizardStyle(QWizard.MacStyle)
            
        elif platform.system() == 'Windows':
            self.wizard.setWizardStyle(QWizard.AeroStyle)
        else:
            self.wizard.setWizardStyle(QWizard.ModernStyle)
        
        # watermark,logo,banner and windowicon for wizard 
        self.wizard.setPixmap(QWizard.WatermarkPixmap,QPixmap('FMI.jeg'))
        self.wizard.setPixmap(QWizard.LogoPixmap,QPixmap('FMI.jeg'))
        self.wizard.setPixmap(QWizard.BannerPixmap,QPixmap('FMI.jeg'))        
        self.wizard.setWindowIcon(QIcon('FMI.jpeg'))
        
        # setting up the first page of wizard with title and subtitile
        page1 = QWizardPage()
        page1.setTitle('FMU Initialization')
        page1.setSubTitle('Enter the below details')
        
        # setting up the page 1 vertical BoxLayout
        vLayout1 = QVBoxLayout(page1)
        
        # adding required widgets for the page 1
        vLayout1.addWidget(self.labelModelName)
        vLayout1.addWidget(self.lineEditModelName)
        vLayout1.addWidget(self.labeldescription)
        vLayout1.addWidget(self.lineEditdescription)
        vLayout1.addWidget(self.pushbuttonClearContentClicked)
        vLayout1.addWidget(self.labelTargetDir)
        
        # setting up page 1 horizontal BoxLayout
        hLayout1 = QHBoxLayout(page1)
        hLayout1.addWidget(self.lineEditTargetDir)
        hLayout1.addWidget(self.pushButtondestination)
        hLayout1.setStretch(0,1)      
        vLayout1.addLayout(hLayout1)
        
        # setting up the tool tips for page 1
        QToolTip.setFont(QFont('SansSerif', 10))
        self.lineEditModelName.setToolTip('Write new Model Name')
        self.lineEditdescription.setToolTip('Provide a new description') 
        self.pushButtondestination.setToolTip('Click to choose the directory') 
        
        # place holder text 
        self.lineEditModelName.setPlaceholderText('Eg: ModelName')
        
        # validating the entered ModelName
        self.validating(self.lineEditModelName)
        
        # setting up the pushButton for choosing the Target director location
        self.pushButtondestination.setIcon(QtGui.QIcon('FMI.jpeg'))          
        #self.pushButtondestination.setText("...")
        self.pushButtondestination.clicked.connect(self.selectFolder)
        
        # setting up page 2 of the wizard    
        page2 = QWizardPage()
        page2.setFinalPage(True)
        
        
        # setting up the page 2 vertical BoxLayout
        vLayout2 = QVBoxLayout(page2)
        #vLayout2.addWidget(label1)
        
        # parsing ModelName to page2 of wizard
        page1.registerField('Field1*',self.lineEditModelName,self.lineEditModelName.text(),self.lineEditModelName.textChanged)
        page1.registerField('Field2*',self.lineEditTargetDir,self.lineEditTargetDir.text(),self.lineEditTargetDir.textChanged)
        
        # setting up the NextButton
        nxt = self.wizard.button(QWizard.NextButton)
        
        # activation of NextButton after lineEditModelName and lineEditTargetDir fields are filled
        func1 = lambda:page2.setTitle('FMU Inputs for ' + page1.field('Field1') + ':')
        func2 = lambda:page1.field('Field2') 
        nxt.clicked.connect(func1)
        nxt.clicked.connect(func2)
    
        # setting up the pushButton for clearing the text in lineEditdescription
        self.pushbuttonClearContentClicked.setText("Clear")
        self.pushbuttonClearContentClicked.clicked.connect(self.qpushbuttonClearContentClicked)
        
        # adding wizard pages
        self.wizard.addPage(page1)
        self.wizard.addPage(page2)
        
        # showing wizard
        self.wizard.show()
        app.exec_()
        
        self.callFMIGenerator()
        
       
    def validating(self,text):
        """ to validate the ModelName entered
        """
        regex = QtCore.QRegExp("[a-z-A-Z_äÄöÖüÜ§$%&()=#+;,0-9]+")
        validator = QRegExpValidator(regex)   
        text.setValidator(validator)
        
    def qpushbuttonClearContentClicked(self):
        # clear the content of the 'QLineEdit'
        self.lineEditdescription.clear()
        # gets the current contents of the 'QLineEdit'
        current_content = self.lineEditdescription    
    
    def selectFolder(self):
        """ to choose the valid directory path
        """
        filepath = QFileDialog.getExistingDirectory(None, "Select Directory")
        # check if user canceled the dialog, if it was canceled, string is empty and we do nothing
        if filepath == "":
            return 

        # set new filepath in line edit
        self.lineEditTargetDir.setText(filepath)
        
    def callFMIGenerator(self):
        
        fmiGenerator = FMIGenerator()
        
        fmiGenerator.modelName = str(self.lineEditModelName.text())
        fmiGenerator.targetDir = self.lineEditTargetDir.text()
        if str(self.lineEditdescription) != None:
            fmiGenerator.description = str(self.lineEditdescription)
        else:
            print ("WARNING: Model description missing.")
            
        # call function of generator to create model
        try:
            fmiGenerator.generate()
        except Exception as e:
            print ("ERROR: Error during FMU generation")
            print e         

            
        
if __name__ == '__main__':
        
    app = QApplication(sys.argv) 
    g = GUI()
    m = g.QWizardPage()
    

 
     
    

