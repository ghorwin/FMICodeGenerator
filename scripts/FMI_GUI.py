import sys
import os
import platform
import PyQt5
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtWidgets import QMessageBox
import os.path

from PyQt5.QtWidgets import QApplication, QMainWindow, QGridLayout, QWidget, QTableWidget, QTableWidgetItem,QWizardPage
from PyQt5.QtCore import QSize, Qt

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QApplication.translate(context, text, disambig)

class Ui_Wizard(object):
    def setupUi(self, Wizard):
        Wizard.setObjectName(_fromUtf8("Wizard"))
        Wizard.resize(510, 439)
        self.wizardPage1 = QWizardPage()
        self.wizard = QWizard()
        self.wizardPage1.setObjectName(_fromUtf8("wizardPage1"))
        self.lineEdit = QLineEdit(self.wizardPage1)
        self.lineEdit.setGeometry(QtCore.QRect(0, 20, 491, 25))
        self.lineEdit.setToolTip(_fromUtf8(""))
        self.lineEdit.setInputMethodHints(QtCore.Qt.ImhSensitiveData)
        self.lineEdit.setText(_fromUtf8(""))
        self.lineEdit.setPlaceholderText(_fromUtf8(""))
        self.lineEdit.setObjectName(_fromUtf8("lineEdit"))
        self.textEdit = QTextEdit(self.wizardPage1)
        self.textEdit.setGeometry(QtCore.QRect(0, 70, 491, 211))
        self.textEdit.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByKeyboard|QtCore.Qt.LinksAccessibleByMouse|QtCore.Qt.TextBrowserInteraction|QtCore.Qt.TextEditable|QtCore.Qt.TextEditorInteraction|QtCore.Qt.TextSelectableByKeyboard|QtCore.Qt.TextSelectableByMouse)
        self.textEdit.setPlaceholderText(_fromUtf8(""))
        self.textEdit.setObjectName(_fromUtf8("textEdit"))
        self.ModelName = QLabel(self.wizardPage1)
        self.ModelName.setGeometry(QtCore.QRect(0, 0, 91, 17))
        self.ModelName.setObjectName(_fromUtf8("ModelName"))
        self.toolButton = QToolButton(self.wizardPage1)
        self.toolButton.setGeometry(QtCore.QRect(460, 340, 26, 24))
        self.toolButton.setObjectName(_fromUtf8("toolButton"))
        self.lineEdit_2 = QLineEdit(self.wizardPage1)
        self.lineEdit_2.setGeometry(QtCore.QRect(0, 340, 451, 25))
        self.lineEdit_2.setObjectName(_fromUtf8("lineEdit_2"))
        self.pushButton = QPushButton(self.wizardPage1)
        self.pushButton.setGeometry(QtCore.QRect(0, 290, 491, 25))
        self.pushButton.setCheckable(False)
        self.pushButton.setObjectName(_fromUtf8("pushButton"))
        self.label = QLabel(self.wizardPage1)
        self.label.setGeometry(QtCore.QRect(0, 50, 81, 17))
        self.label.setObjectName(_fromUtf8("label"))
        self.label_2 = QLabel(self.wizardPage1)
        self.label_2.setGeometry(QtCore.QRect(0, 320, 121, 17))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.kdialog = QDialog(self.wizardPage1)
        self.kdialog.setGeometry(QtCore.QRect(60, 120, 361, 121))
        self.kdialog.setSizeGripEnabled(False)
        self.kdialog.setModal(False)
        self.kdialog.setObjectName(_fromUtf8("kdialog"))
        self.buttonBox = QDialogButtonBox(self.kdialog)
        self.buttonBox.setGeometry(QtCore.QRect(110, 70, 166, 25))
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.buttonBox.sizePolicy().hasHeightForWidth())
        self.buttonBox.setSizePolicy(sizePolicy)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)
        self.buttonBox.setCenterButtons(True)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.label_3 = QLabel(self.kdialog)
        self.label_3.setGeometry(QtCore.QRect(90, 30, 201, 20))
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_3.sizePolicy().hasHeightForWidth())
        self.label_3.setSizePolicy(sizePolicy)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        Wizard.addPage(self.wizardPage1)
        self.wizardPage2 = QWizardPage()
        self.wizardPage2.setObjectName(_fromUtf8("wizardPage2"))
        self.tableWidget = QTableWidget(self.wizardPage2)
        self.tableWidget.setGeometry(QtCore.QRect(0, 10, 491, 141))
        sizePolicy = QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tableWidget.sizePolicy().hasHeightForWidth())
        self.tableWidget.setSizePolicy(sizePolicy)
        self.tableWidget.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.tableWidget.setAutoFillBackground(True)
        self.tableWidget.setLineWidth(1)
        self.tableWidget.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.tableWidget.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.tableWidget.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        self.tableWidget.setTabKeyNavigation(False)
        self.tableWidget.setAlternatingRowColors(False)
        self.tableWidget.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.tableWidget.setShowGrid(True)
        self.tableWidget.setGridStyle(QtCore.Qt.SolidLine)
        self.tableWidget.setRowCount(3)
        self.tableWidget.setObjectName(_fromUtf8("tableWidget"))
        self.tableWidget.setColumnCount(4)
        item = QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        font = QFont()
        font.setBold(True)
        font.setWeight(75)
        item.setFont(font)
        self.tableWidget.setHorizontalHeaderItem(0, item)
        item = QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        font = QFont()
        font.setBold(True)
        font.setWeight(75)
        item.setFont(font)
        self.tableWidget.setHorizontalHeaderItem(1, item)
        item = QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        font = QFont()
        font.setBold(True)
        font.setWeight(75)
        item.setFont(font)
        self.tableWidget.setHorizontalHeaderItem(2, item)
        item = QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        font = QFont()
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        font.setStyleStrategy(QFont.PreferDefault)
        item.setFont(font)
        self.tableWidget.setHorizontalHeaderItem(3, item)
        self.tableWidget.horizontalHeader().setVisible(True)
        self.tableWidget.horizontalHeader().setCascadingSectionResizes(True)
        self.tableWidget.horizontalHeader().setDefaultSectionSize(116)
        self.tableWidget.horizontalHeader().setHighlightSections(True)
        self.tableWidget.horizontalHeader().setMinimumSectionSize(68)
        self.tableWidget.horizontalHeader().setSortIndicatorShown(True)
        self.tableWidget.horizontalHeader().setStretchLastSection(True)
        self.tableWidget.verticalHeader().setVisible(False)
        self.tableWidget.verticalHeader().setCascadingSectionResizes(True)
        self.tableWidget.verticalHeader().setDefaultSectionSize(35)
        self.tableWidget.verticalHeader().setMinimumSectionSize(21)
        self.tableWidget.verticalHeader().setSortIndicatorShown(True)
        self.tableWidget.verticalHeader().setStretchLastSection(False)
        self.line = QFrame(self.wizardPage2)
        self.line.setGeometry(QtCore.QRect(0, 160, 491, 16))
        self.line.setFrameShape(QFrame.HLine)
        self.line.setFrameShadow(QFrame.Sunken)
        self.line.setObjectName(_fromUtf8("line"))
        
        
        self.wizardPage1.registerField('Field1*',self.lineEdit,self.lineEdit.text(),self.lineEdit.textChanged)
        self.wizardPage1.registerField('Field2*',self.lineEdit_2,self.lineEdit_2.text(),self.lineEdit_2.textChanged)        
        
        # activation of NextButton after lineEditModelName and lineEditTargetDir fields are filled
        func1 = lambda:self.wizardPage2.setTitle('FMU Inputs for ' + self.wizardPage1.field('Field1') + ':')
        func2 = lambda:self.wizardPage2.field('Field2')         
        
        # setting up the NextButton
        nxt = self.wizard.button(QWizard.NextButton)        
        nxt.clicked.connect(func1)
        nxt.clicked.connect(func2)        
        
               
        
        Wizard.addPage(self.wizardPage2)

        self.retranslateUi(Wizard)
        self.pushButton.clicked.connect(self.textEdit.clear)
        self.kdialog.accepted.connect(self.wizardPage2.show)
        self.kdialog.rejected.connect(self.wizardPage1.show)
        QtCore.QMetaObject.connectSlotsByName(Wizard)

    def retranslateUi(self, Wizard):
        Wizard.setWindowTitle(_translate("Wizard", "FMU", None))
        self.ModelName.setText(_translate("Wizard", "ModelName:", None))
        self.toolButton.setText(_translate("Wizard", "...", None))
        self.pushButton.setText(_translate("Wizard", "Clear", None))
        self.label.setText(_translate("Wizard", "Description:", None))
        self.label_2.setText(_translate("Wizard", "Target Location:", None))
        self.label_3.setText(_translate("Wizard", "Do you want to save changes?", None))
        self.tableWidget.setSortingEnabled(False)
        item = self.tableWidget.horizontalHeaderItem(0)
        item.setText(_translate("Wizard", "Unique ID Name", None))
        item = self.tableWidget.horizontalHeaderItem(1)
        item.setText(_translate("Wizard", "Macro Name", None))
        item = self.tableWidget.horizontalHeaderItem(2)
        item.setText(_translate("Wizard", "Type", None))
        item = self.tableWidget.horizontalHeaderItem(3)
        item.setText(_translate("Wizard", "Properties", None))
        
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

if __name__ == '__main__':
                
    app = QApplication(sys.argv) 
    w=QWizard()
    g = Ui_Wizard()
    m = g.setupUi(w)
    w.show()
    app.exec_() 
