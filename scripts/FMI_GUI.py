import sys
import os
import platform
import PyQt5
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtWidgets import QMessageBox
import os.path
from FMIGenerator import *

class GUI():
    
    def __init__(self):
        """ Constructor, initializes member variables.
        wizard -- To set a Wizard
        ModelName -- A user defined model name
        description -- A user defined description
        TargetDir -- Target directory can be relative (to current working directory) or
					 absolute. FMU directory is created below this directory, for example:
					    <target path>/<modelName>/
					 By default, target path is empty which means that the subdirectory <modelName>
					 is created directly below the current working directory.
        page1 -- Page 1 of Wizard
        page2 -- Page 2 of Wizard
        """
        
        self.wizard = QWizard()
        self.lineEditModelName = QLineEdit()
        self.textEditdescription = QTextEdit()
        self.lineEditTargetDir = QLineEdit()
        self.page1 = QWizardPage()
        self.page2 = QWizardPage()
        
        # Different Wizard based on platform
        if platform.system() == 'Darwin':
            self.wizard.setWizardStyle(QWizard.MacStyle)
            
        elif platform.system() == 'Windows':
            self.wizard.setWizardStyle(QWizard.AeroStyle)
        else:
            self.wizard.setWizardStyle(QWizard.ModernStyle)        
    
        
    def QWizardPage1(self): 
        """ Develops Wizard page 1 for FMUGeneration inputs such as,
        ModelName -- A user defined model name
        description -- A user defined description
        """
        
        # different labels and lineEdit's for Page 1
        self.labelModelName = QLabel('Model Name:')
        self.labeldescription = QLabel('Description:')
        self.labelTargetDir = QLabel('Target Location:')
        self.pushButtondestination = QToolButton()        
        self.pushbuttonClear = QPushButton()         
        
    
        

        # watermark,logo,banner and windowicon for wizard 
        self.page1.setPixmap(QWizard.WatermarkPixmap,QPixmap('FMI.jeg'))
        self.page1.setPixmap(QWizard.LogoPixmap,QPixmap('FMI.jeg'))
        self.page1.setPixmap(QWizard.BannerPixmap,QPixmap('FMI.jeg'))        
        self.wizard.setWindowIcon(QIcon('FMI.jpeg'))
        
        # setting up the first page of wizard with title and subtitile
        self.page1.setTitle('FMU Initialization')
        self.page1.setSubTitle('Enter the below details')
        
        # setting up the page 1 vertical BoxLayout
        vLayout1 = QVBoxLayout(self.page1)
        
        # adding required widgets for the page 1
        vLayout1.addWidget(self.labelModelName)
        vLayout1.addWidget(self.lineEditModelName)
        vLayout1.addWidget(self.labeldescription)
        vLayout1.addWidget(self.textEditdescription)
        vLayout1.addWidget(self.pushbuttonClear)
        vLayout1.addWidget(self.labelTargetDir)
        
        # setting up page 1 horizontal BoxLayout
        hLayout1 = QHBoxLayout(self.page1)
        hLayout1.addWidget(self.lineEditTargetDir)
        hLayout1.addWidget(self.pushButtondestination)
        hLayout1.setStretch(0,1)      
        vLayout1.addLayout(hLayout1)
        
        # setting up the tool tips for page 1
        QToolTip.setFont(QFont('SansSerif', 10))
        self.lineEditModelName.setToolTip('Write new Model Name')
        self.textEditdescription.setToolTip('Provide a new description') 
        self.pushButtondestination.setToolTip('Click to choose the directory') 
        
        # place holder text 
        self.lineEditModelName.setPlaceholderText('Eg: ModelName')
        #self.textEditdescription.setPlaceholderText('This is a test for FMU Generation')
        
        # validating the entered ModelName
        self.validating(self.lineEditModelName)
        
        # setting up the pushButton for clearing the text in lineEditdescription
        self.pushbuttonClear.setText("Clear")
        self.pushbuttonClear.clicked.connect(self.pushbuttonClearContentClicked)   
            
    
        # setting up the pushButton for choosing the Target director location
        self.pushButtondestination.setIcon(QtGui.QIcon('FMI.jpeg'))          
        #self.pushButtondestination.setText("...")
        self.pushButtondestination.clicked.connect(self.selectFolder)
        
        
        # parsing ModelName to page2 of wizard
        self.page1.registerField('Field1*',self.lineEditModelName,self.lineEditModelName.text(),self.lineEditModelName.textChanged)
        self.page1.registerField('Field2*',self.lineEditTargetDir,self.lineEditTargetDir.text(),self.lineEditTargetDir.textChanged)
       
        # setting up the NextButton
        nxt = self.wizard.button(QWizard.NextButton)
        
        # activation of NextButton after lineEditModelName and lineEditTargetDir fields are filled
        func1 = lambda:self.page2.setTitle('FMU Inputs for ' + self.page1.field('Field1') + ':')
        func2 = lambda:self.page2.field('Field2')
        
        
         
        
        nxt.clicked.connect(func1)
        nxt.clicked.connect(func2)   
        
        nxt.clicked.connect(self.descriptionError)
        nxt.clicked.connect(self.clickMethod)          
        
        
        # adding wizard pages
        self.wizard.addPage(self.page1)
        
    
        # calling the defined function for wizard page2
        self.QWizardPage2()
        
        
        # command to show the wizard pages
        self.wizard.show()
        app.exec_() 
        
        
        # calling the defined function to generate FMU
        self.callFMIGenerator()          
    
           
        
    def QWizardPage2(self):
        """ Develops Wizard page 2 for FMUGeneration inputs such as,
        InputVal1 -- A user defined input value 1
        InputVal2 -- A user defined input value 2
        progress -- A progress Bar
        """        
        # setting up page 2 of the wizard    
        self.page2.setFinalPage(True)

        
        # setting up the three input labels and lineEdit's
        self.labelInputVar1 = QLabel("Input Var1:")
        self.lineEditInputVal11 = QLineEdit()
        self.lineEditInputVal12 = QLineEdit()
        self.lineEditInputVal13 = QLineEdit()
        self.lineEditInputVal14 = QLineEdit()
        
        
        self.labelInputVar2 = QLabel("Input Var2:")
        self.lineEditInputVal21 = QLineEdit()
        self.lineEditInputVal22 = QLineEdit()
        self.lineEditInputVal23 = QLineEdit()
        self.lineEditInputVal24 = QLineEdit()        
        
        
        self.labelInputVar3 = QLabel("Input Var3:")
        self.lineEditInputVal31 = QLineEdit()
        self.lineEditInputVal32 = QLineEdit()
        self.lineEditInputVal33 = QLineEdit()
        self.lineEditInputVal34 = QLineEdit()        
        
     
        
        # setting up page 2 vertical and horizontal BoxLayout
        vLayout2 = QVBoxLayout(self.page2)
        
        
        # for input Variable 1
        hLayout21 = QHBoxLayout(self.page2)
        hLayout21.addWidget(self.labelInputVar1)
        hLayout21.addWidget(self.lineEditInputVal11)
        hLayout21.addWidget(self.lineEditInputVal12)
        hLayout21.addWidget(self.lineEditInputVal13)
        hLayout21.addWidget(self.lineEditInputVal14)
        hLayout21.addStretch(1)
        hLayout21.addStretch(2) 
        vLayout2.addLayout(hLayout21)
        
        # for input Variable 2
        hLayout22 = QHBoxLayout(self.page2)
        hLayout22.addWidget(self.labelInputVar2)
        hLayout22.addWidget(self.lineEditInputVal21)
        hLayout22.addWidget(self.lineEditInputVal22)
        hLayout22.addWidget(self.lineEditInputVal23)
        hLayout22.addWidget(self.lineEditInputVal24)        
        hLayout22.addStretch(1)  
        vLayout2.addLayout(hLayout22)
        
        # for input Variable 3
        hLayout23 = QHBoxLayout(self.page2)
        hLayout23.addWidget(self.labelInputVar3)
        hLayout23.addWidget(self.lineEditInputVal31)
        hLayout23.addWidget(self.lineEditInputVal32)
        hLayout23.addWidget(self.lineEditInputVal33)
        hLayout23.addWidget(self.lineEditInputVal34) 
        hLayout23.addStretch(1)  
        vLayout2.addLayout(hLayout23)        
        

        # setting up the two paramter labels and lineEdit's
        self.labelparameterVar1 = QLabel("Parameter 1:")
        self.lineEditparameterVal11 = QLineEdit()
        self.lineEditparameterVal12 = QLineEdit()
        
        
        
        self.labelparameterVar2 = QLabel("Parameter 2:")
        self.lineEditparameterVal21 = QLineEdit()
        self.lineEditparameterVal22 = QLineEdit()
                
        
        
        self.labelparameterVar3 = QLabel("Parameter 3:")
        self.lineEditparameterVal31 = QLineEdit()
        self.lineEditparameterVal32 = QLineEdit()
               
    
        
        # for parameter Variable 1
        hLayout24 = QHBoxLayout(self.page2)
        hLayout24.addWidget(self.labelparameterVar1)
        hLayout24.addWidget(self.lineEditparameterVal11)
        hLayout24.addWidget(self.lineEditparameterVal12)
        hLayout24.addStretch(1)
        hLayout24.addStretch(2) 
        vLayout2.addLayout(hLayout24)
        
        # for parameter Variable 2
        hLayout25 = QHBoxLayout(self.page2)
        hLayout25.addWidget(self.labelparameterVar2)
        hLayout25.addWidget(self.lineEditparameterVal21)
        hLayout25.addWidget(self.lineEditparameterVal22)
                
        hLayout25.addStretch(1)  
        vLayout2.addLayout(hLayout25)
        
        # for parameter Variable 3
        hLayout26 = QHBoxLayout(self.page2)
        hLayout26.addWidget(self.labelparameterVar3)
        hLayout26.addWidget(self.lineEditparameterVal31)
        hLayout26.addWidget(self.lineEditparameterVal32)
        hLayout26.addStretch(1)  
        vLayout2.addLayout(hLayout26)                
        
        
        
        # setting up the three output labels and lineEdit's
        self.labeloutputVar1 = QLabel("Output Var1:")
        self.lineEditoutputVal11 = QLineEdit()
        self.lineEditoutputVal12 = QLineEdit()
        
        
        
        self.labeloutputVar2 = QLabel("Output Var2:")
        self.lineEditoutputVal21 = QLineEdit()
        self.lineEditoutputVal22 = QLineEdit()
                
        
        
        self.labeloutputVar3 = QLabel("Output Var3:")
        self.lineEditoutputVal31 = QLineEdit()
        self.lineEditoutputVal32 = QLineEdit()
               
    
        
        
        # for output Variable 1
        hLayout24.addWidget(self.labeloutputVar1)
        hLayout24.addWidget(self.lineEditoutputVal11)
        hLayout24.addWidget(self.lineEditoutputVal12)
        hLayout24.addStretch(2) 
        vLayout2.addLayout(hLayout24)
        
        # for output Variable 2
        
        hLayout25.addWidget(self.labeloutputVar2)
        hLayout25.addWidget(self.lineEditoutputVal21)
        hLayout25.addWidget(self.lineEditoutputVal22)
        hLayout25.addStretch(1)  
        vLayout2.addLayout(hLayout25)
        
        # for output Variable 3
        
        hLayout26.addWidget(self.labeloutputVar3)
        hLayout26.addWidget(self.lineEditoutputVal31)
        hLayout26.addWidget(self.lineEditoutputVal32)
        hLayout26.addStretch(1)  
        vLayout2.addLayout(hLayout26)                
       
   
       
        self.progress = QProgressBar()
         
        # for progressBar  
        vLayout2.addStretch()
        vLayout2.addWidget(self.progress)
        self.btn = QPushButton("Okay")
        vLayout2.addWidget(self.btn)
        self.btn.clicked.connect(self.progressbar)
        
        # adding  Page2 to wizard
        self.wizard.addPage(self.page2)
        
        
        
    def progressbar(self):
        self.completed = 0
        while self.completed < 100:
            self.completed+=0.0001
            self.progress.setValue(self.completed)

    def validating(self,text):
        """ to validate the ModelName entered
        """
        regex = QtCore.QRegExp("[a-z-A-Z_äÄöÖüÜ§$%&()=#+;,0-9]+")
        validator = QRegExpValidator(regex)   
        text.setValidator(validator)
    
    def clickMethod(self):
        msgBox = QMessageBox()
        
        msgBox.setIcon(QMessageBox.Question)
        msgBox.setText("The file name and pathname have been modified")
        msgBox.setInformativeText("Do you want to save your changes?")
        msgBox.setStandardButtons(QMessageBox.Yes| QMessageBox.No| QMessageBox.Cancel  )
        msgBox.setDefaultButton(QMessageBox.No)
        reply = msgBox.exec_()
        if reply == QMessageBox.Yes:
            return "yes"
        elif reply == QMessageBox.No:
            return "no"
        else:
            return "cancel"
    
       
        
    def pushbuttonClearContentClicked(self):
        """ to clear the content in lineEditdecription 
        """       
        # clear the content of the 'QLineEdit'
        self.textEditdescription.clear()
        # gets the current contents of the 'QLineEdit'
        current_content = self.textEditdescription    
    
    def selectFolder(self):
        """ to choose the valid directory path
        """
        filepath = QFileDialog.getExistingDirectory(None, "Select Directory")
        # check if user canceled the dialog, if it was canceled, string is empty and we do nothing
        if filepath == "":
            return 

        # set new filepath in line edit
        self.lineEditTargetDir.setText(filepath)
        
    def descriptionError(self):
        # user defined description from wizard 
        if self.textEditdescription.toPlainText() != "":
            print self.textEditdescription.toPlainText()  
        else:
            print ("WARNING: Model description missing.")
            msgBox = QMessageBox()        
            msgBox.setIcon(QMessageBox.Question)
            msgBox.setText("WARNING: Model description missing.")
            msgBox.setInformativeText("Do you want to quit?")
            msgBox.setStandardButtons(QMessageBox.Cancel  )
            msgBox.setDefaultButton(QMessageBox.No)
            reply = msgBox.exec_()
            if reply == QMessageBox.Cancel:
                return "Cancel"        
    
        
    def callFMIGenerator(self):
        """ calling the FMIGenerator.py script to generate and test build the FMU
        """
        
        # create storage class instance 
        fmiGenerator = FMIGenerator()
        
        # gets user input modelName and target directory from wizard
        fmiGenerator.modelName = str(self.lineEditModelName.text())
        
        fmiGenerator.targetDir = self.lineEditTargetDir.text()
        fmiGenerator.description = self.textEditdescription.toPlainText()
                         
        # call function of generator to create model
        try:
            fmiGenerator.generate()
        except Exception as e:
            print ("ERROR: Error during FMU generation")
            print e        
              
if __name__ == '__main__':
        
    app = QApplication(sys.argv) 
    g = GUI()
    m = g.QWizardPage1()
    

 
     
    

