import sys
import PyQt5
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

# CREATE WIZARD, WATERMARK, LOGO, BANNER
app = QApplication(sys.argv)
wizard = QWizard()
wizard.setWizardStyle(QWizard.ModernStyle)

wizard.setPixmap(QWizard.WatermarkPixmap,QPixmap('FM.png'))
wizard.setPixmap(QWizard.LogoPixmap,QPixmap('FM.png'))
wizard.setPixmap(QWizard.BannerPixmap,QPixmap('FM.png'))
wizard.setWindowIcon(QIcon('FMI.png')) 


page1 = QWizardPage()
page1.setTitle('FMU Initialization')
page1.setSubTitle('Please enter the below details')

modelName = QLabel('Model Name:')
description = QLabel('Description:')          
modelNameEdit = QLineEdit()
descriptionEdit = QLineEdit()

lineEdit = QLineEdit()
vLayout1 = QVBoxLayout(page1)
vLayout1.addWidget(modelName)
vLayout1.addWidget(modelNameEdit)

#hLayout3 = QHBoxLayout(page1)
vLayout1.addWidget(description)
vLayout1.addWidget(descriptionEdit)

page1.registerField('Field1*',modelNameEdit,modelNameEdit.text(),modelNameEdit.textChanged)
page1.registerField('Field2',descriptionEdit,descriptionEdit.text(),descriptionEdit.textChanged)

# CREATE PAGE 2, LABEL, TITLES
page2 = QWizardPage()
page2.setFinalPage(True)

page2.setTitle('FMU Page 2')
page2.setSubTitle('Fasih!')

label1 = QLabel()
label2 = QLabel()

vLayout2 = QVBoxLayout(page2)

vLayout2.addWidget(label1)
vLayout2.addWidget(label2)


QToolTip.setFont(QFont('SansSerif', 10))
modelNameEdit.setToolTip('Write new Model Name')
descriptionEdit.setToolTip('Provide a new description')





# CONNECT SIGNALS AND PAGES
# lineEdit.textChanged.connect(lambda:label.setText(lineEdit.text()))
nxt = wizard.button(QWizard.NextButton)
func1 = lambda:label1.setText(page1.field('Field1'))
func2 = lambda:label2.setText(page1.field('Field2'))
nxt.clicked.connect(func1)
nxt.clicked.connect(func2)

wizard.addPage(page1)
wizard.addPage(page2)

wizard.show()
sys.exit(app.exec_())