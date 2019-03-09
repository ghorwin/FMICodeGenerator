# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'WizardPageGenerate.ui'
#
# Created by: PyQt5 UI code generator 5.5.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_WizardPageGenerate(object):
	def setupUi(self, WizardPageGenerate):
		WizardPageGenerate.setObjectName("WizardPageGenerate")
		WizardPageGenerate.resize(400, 300)
		self.verticalLayout_2 = QtWidgets.QVBoxLayout(WizardPageGenerate)
		self.verticalLayout_2.setObjectName("verticalLayout_2")
		self.checkBoxTestBuild = QtWidgets.QCheckBox(WizardPageGenerate)
		self.checkBoxTestBuild.setChecked(True)
		self.checkBoxTestBuild.setObjectName("checkBoxTestBuild")
		self.verticalLayout_2.addWidget(self.checkBoxTestBuild)
		self.groupBox = QtWidgets.QGroupBox(WizardPageGenerate)
		self.groupBox.setObjectName("groupBox")
		self.verticalLayout = QtWidgets.QVBoxLayout(self.groupBox)
		self.verticalLayout.setObjectName("verticalLayout")
		self.plainTextEditLog = QtWidgets.QPlainTextEdit(self.groupBox)
		self.plainTextEditLog.setObjectName("plainTextEditLog")
		self.verticalLayout.addWidget(self.plainTextEditLog)
		self.verticalLayout_2.addWidget(self.groupBox)

		self.retranslateUi(WizardPageGenerate)
		QtCore.QMetaObject.connectSlotsByName(WizardPageGenerate)

	def retranslateUi(self, WizardPageGenerate):
		_translate = QtCore.QCoreApplication.translate
		WizardPageGenerate.setWindowTitle(_translate("WizardPageGenerate", "Form"))
		self.checkBoxTestBuild.setText(_translate("WizardPageGenerate", "Test-build FMU after code generation"))
		self.groupBox.setTitle(_translate("WizardPageGenerate", "Generation log"))

