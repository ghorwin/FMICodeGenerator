# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'WizardPageBasicProperties.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_WizardPageBasicProperties(object):
	def setupUi(self, WizardPageBasicProperties):
		WizardPageBasicProperties.setObjectName("WizardPageBasicProperties")
		WizardPageBasicProperties.resize(699, 361)
		self.verticalLayout_2 = QtWidgets.QVBoxLayout(WizardPageBasicProperties)
		self.verticalLayout_2.setObjectName("verticalLayout_2")
		self.groupBox_2 = QtWidgets.QGroupBox(WizardPageBasicProperties)
		self.groupBox_2.setObjectName("groupBox_2")
		self.gridLayout = QtWidgets.QGridLayout(self.groupBox_2)
		self.gridLayout.setObjectName("gridLayout")
		self.label_2 = QtWidgets.QLabel(self.groupBox_2)
		self.label_2.setObjectName("label_2")
		self.gridLayout.addWidget(self.label_2, 2, 0, 1, 1)
		self.label = QtWidgets.QLabel(self.groupBox_2)
		self.label.setObjectName("label")
		self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
		self.lineEditModelName = QtWidgets.QLineEdit(self.groupBox_2)
		self.lineEditModelName.setObjectName("lineEditModelName")
		self.gridLayout.addWidget(self.lineEditModelName, 0, 1, 1, 2)
		self.lineEditTargetDir = QtWidgets.QLineEdit(self.groupBox_2)
		self.lineEditTargetDir.setObjectName("lineEditTargetDir")
		self.gridLayout.addWidget(self.lineEditTargetDir, 2, 1, 1, 1)
		self.toolButtonBrowseFilename = QtWidgets.QToolButton(self.groupBox_2)
		self.toolButtonBrowseFilename.setObjectName("toolButtonBrowseFilename")
		self.gridLayout.addWidget(self.toolButtonBrowseFilename, 2, 2, 1, 1)
		self.label_3 = QtWidgets.QLabel(self.groupBox_2)
		font = QtGui.QFont()
		font.setItalic(True)
		self.label_3.setFont(font)
		self.label_3.setObjectName("label_3")
		self.gridLayout.addWidget(self.label_3, 3, 1, 1, 1)
		self.label_4 = QtWidgets.QLabel(self.groupBox_2)
		font = QtGui.QFont()
		font.setItalic(True)
		self.label_4.setFont(font)
		self.label_4.setObjectName("label_4")
		self.gridLayout.addWidget(self.label_4, 1, 1, 1, 1)
		self.label_5 = QtWidgets.QLabel(self.groupBox_2)
		self.label_5.setObjectName("label_5")
		self.gridLayout.addWidget(self.label_5, 4, 0, 1, 1)
		self.lineEditFMUFilePath = QtWidgets.QLineEdit(self.groupBox_2)
		self.lineEditFMUFilePath.setReadOnly(True)
		self.lineEditFMUFilePath.setObjectName("lineEditFMUFilePath")
		self.gridLayout.addWidget(self.lineEditFMUFilePath, 4, 1, 1, 1)
		self.verticalLayout_2.addWidget(self.groupBox_2)
		self.groupBox = QtWidgets.QGroupBox(WizardPageBasicProperties)
		self.groupBox.setObjectName("groupBox")
		self.verticalLayout = QtWidgets.QVBoxLayout(self.groupBox)
		self.verticalLayout.setObjectName("verticalLayout")
		self.plainTextEditDescription = QtWidgets.QPlainTextEdit(self.groupBox)
		self.plainTextEditDescription.setObjectName("plainTextEditDescription")
		self.verticalLayout.addWidget(self.plainTextEditDescription)
		self.verticalLayout_2.addWidget(self.groupBox)

		self.retranslateUi(WizardPageBasicProperties)
		QtCore.QMetaObject.connectSlotsByName(WizardPageBasicProperties)

	def retranslateUi(self, WizardPageBasicProperties):
		_translate = QtCore.QCoreApplication.translate
		WizardPageBasicProperties.setWindowTitle(_translate("WizardPageBasicProperties", "Form"))
		self.groupBox_2.setTitle(_translate("WizardPageBasicProperties", "Required properties"))
		self.label_2.setText(_translate("WizardPageBasicProperties", "Output directory:"))
		self.label.setText(_translate("WizardPageBasicProperties", "Name:"))
		self.toolButtonBrowseFilename.setText(_translate("WizardPageBasicProperties", "..."))
		self.label_3.setText(_translate("WizardPageBasicProperties", "Output directory can be an absolute or relative path."))
		self.label_4.setText(_translate("WizardPageBasicProperties", "Model name must not contain whitespace characters."))
		self.label_5.setText(_translate("WizardPageBasicProperties", "FMU directory:"))
		self.groupBox.setTitle(_translate("WizardPageBasicProperties", "Description"))

