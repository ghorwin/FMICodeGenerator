#!/usr/bin/python
# -*- coding: utf-8 -*-

# Implementation of the variable definition wizard page.
#
#
# This file is part of FMICodeGenerator (https://github.com/ghorwin/FMICodeGenerator)
#
# BSD 3-Clause License
#
# Copyright (c) 2018, Andreas Nicolai
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
# * Neither the name of the copyright holder nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import sys
from PyQt5.QtWidgets import QWidget, QTableWidgetItem
from PyQt5.QtCore import pyqtSlot, Qt

from ui.Ui_WizardPageVariables import Ui_WizardPageVariables

from FMIGenerator import FMIGenerator, VarDef, varDefFromJson

class WizardPageVariables(QWidget):
	def __init__(self):
		super(WizardPageVariables, self).__init__()
		self.ui = Ui_WizardPageVariables()
		self.ui.setupUi(self)
		
		self.ui.groupBox_2.setEnabled(False) # disabled by default
		self.variables = []
		
		# add default variable
		newVar = VarDef("ResultRootDir", "fixed", "parameter", "exact", "String")
		newVar.valueRef = 42
		newVar.startValue = "" # start value is empty, this parameter is automatically supplied by MasterSim
		
		self.variables.append(newVar)
		
		self.updateTable()
		self.ui.tableWidget.selectRow(0)
		self.show()

	def updateTable(self):
		"""Syncronizes self.variables with table widget"""
		
		self.ui.tableWidget.setRowCount(len(self.variables))
		for i in range(len(self.variables)):
			var = self.variables[i]
			
			item = QTableWidgetItem()
			item.setFlags( Qt.ItemIsSelectable | Qt.ItemIsEnabled)
			item.setText(var.name)
			self.ui.tableWidget.setItem(i, 0, item)
			
			item = QTableWidgetItem()
			item.setText("{}".format(var.valueRef))
			item.setFlags( Qt.ItemIsSelectable | Qt.ItemIsEnabled)
			self.ui.tableWidget.setItem(i, 1, item)
			
			item = QTableWidgetItem()
			item.setText(var.variability)
			item.setFlags( Qt.ItemIsSelectable | Qt.ItemIsEnabled)
			self.ui.tableWidget.setItem(i, 2, item)
			
			item = QTableWidgetItem()
			item.setText(var.causality)
			item.setFlags( Qt.ItemIsSelectable | Qt.ItemIsEnabled)
			self.ui.tableWidget.setItem(i, 3, item)
			
			item = QTableWidgetItem()
			item.setText(var.initial)
			item.setFlags( Qt.ItemIsSelectable | Qt.ItemIsEnabled)
			self.ui.tableWidget.setItem(i, 4, item)
			
			item = QTableWidgetItem()
			item.setText(var.typeID)
			item.setFlags( Qt.ItemIsSelectable | Qt.ItemIsEnabled)
			self.ui.tableWidget.setItem(i, 5, item)

			item = QTableWidgetItem()
			item.setText("{}".format(var.startValue))
			item.setFlags( Qt.ItemIsSelectable | Qt.ItemIsEnabled)
			self.ui.tableWidget.setItem(i, 6, item)
			
		self.ui.tableWidget.resizeColumnsToContents()

	
	def updateEditField(self, var):
		self.ui.groupBox_2.setEnabled(True)
		
		self.ui.lineEditName.setText(var.name)
		self.ui.spinBoxValueRef.setValue(var.valueRef)
		self.ui.comboBoxCausality.setCurrentIndex( self.ui.comboBoxCausality.findText(var.causality) )
		self.ui.comboBoxVariability.setCurrentIndex( self.ui.comboBoxVariability.findText(var.variability) )
		self.ui.comboBoxInitial.setCurrentIndex( self.ui.comboBoxInitial.findText(var.initial) )
		self.ui.comboBoxTypeID.setCurrentIndex( self.ui.comboBoxTypeID.findText(var.typeID) )
		self.ui.lineEditStart.setText( var.startValue )
	
	@pyqtSlot(str)
	def onLoadDefaults(self, inputDataFile):
		fmiGenerator = FMIGenerator()
		fmiGenerator.readInputData(inputDataFile)
		self.variables = fmiGenerator.variables
		self.updateTable()
		

	@pyqtSlot()
	def on_toolButtonAdd_clicked(self):
		# add a new table row and enabled edit field
		currentVarCount = self.ui.tableWidget.rowCount()
		
		newVar = VarDef("unnamed", "continuous", "local", "exact", "Real")
		self.variables.append(newVar)
		
		# update table
		self.updateTable()
		
		# select last line, this will trigger the edit field population
		self.ui.tableWidget.selectRow(len(self.variables)-1)


	@pyqtSlot()
	def on_toolButtonRemove_clicked(self):
		# get current row
		currentRow = self.ui.tableWidget.currentRow()
		assert(currentRow >= 0 and currentRow < len(self.variables))

		# remove selected variable
		del self.variables[currentRow]
		# update table
		self.updateTable()
		# select next row
		if currentRow >= len(self.variables):
			currentRow = currentRow -1
		if currentRow >= 0:
			self.ui.tableWidget.selectRow(currentRow)


	@pyqtSlot(QTableWidgetItem, QTableWidgetItem)
	def on_tableWidget_currentItemChanged(self, current, previous):
		# get current row
		currentRow = self.ui.tableWidget.currentRow()
		# get corresponding variable
		if currentRow < 0:
			# disable edit fields
			self.ui.groupBox_2.setEnabled(False) 
			# disable remove
			self.ui.toolButtonRemove.setEnabled(False) 
			return # no selection, return
		
		assert(currentRow < len(self.variables))
		
		# enable remove button
		self.ui.toolButtonRemove.setEnabled(True) 
		
		# fill in edit fields
		self.updateEditField(self.variables[currentRow])
		
		
	@pyqtSlot(str)
	def on_lineEditName_textEdited(self,text):
		# get current row
		currentRow = self.ui.tableWidget.currentRow()
		assert(currentRow >= 0 and currentRow < len(self.variables))
		# update variable cache
		self.variables[currentRow].name = text
		# changing a property of a QTableWidgetItem requires removal of item, change of property and re-setting the item
		item = self.ui.tableWidget.takeItem(currentRow,0)
		item.setText(text)
		self.ui.tableWidget.setItem(currentRow,0,item)
		self.ui.tableWidget.resizeColumnToContents(0)
		
		
	@pyqtSlot(int)
	def on_spinBoxValueRef_valueChanged(self, value):
		# get current row
		currentRow = self.ui.tableWidget.currentRow()
		assert(currentRow >= 0 and currentRow < len(self.variables))
		# update variable cache
		self.variables[currentRow].valueRef = value
		# changing a property of a QTableWidgetItem requires removal of item, change of property and re-setting the item
		item = self.ui.tableWidget.takeItem(currentRow,1)
		item.setText("{}".format(value))
		self.ui.tableWidget.setItem(currentRow,1,item)
		self.ui.tableWidget.resizeColumnToContents(1)


	@pyqtSlot(str)
	def on_comboBoxVariability_currentIndexChanged(self, text):
		# get current row
		currentRow = self.ui.tableWidget.currentRow()
		assert(currentRow >= 0 and currentRow < len(self.variables))
		# update variable cache
		self.variables[currentRow].variability = text
		# changing a property of a QTableWidgetItem requires removal of item, change of property and re-setting the item
		item = self.ui.tableWidget.takeItem(currentRow,2)
		item.setText(text)
		self.ui.tableWidget.setItem(currentRow,2,item)
		self.ui.tableWidget.resizeColumnToContents(2)


	@pyqtSlot(str)
	def on_comboBoxCausality_currentIndexChanged(self, text):
		# get current row
		currentRow = self.ui.tableWidget.currentRow()
		assert(currentRow >= 0 and currentRow < len(self.variables))
		# update variable cache
		self.variables[currentRow].causality = text
		# changing a property of a QTableWidgetItem requires removal of item, change of property and re-setting the item
		item = self.ui.tableWidget.takeItem(currentRow,3)
		item.setText(text)
		self.ui.tableWidget.setItem(currentRow,3,item)
		self.ui.tableWidget.resizeColumnToContents(3)


	@pyqtSlot(str)
	def on_comboBoxInitial_currentIndexChanged(self, text):
		# get current row
		currentRow = self.ui.tableWidget.currentRow()
		assert(currentRow >= 0 and currentRow < len(self.variables))
		# update variable cache
		self.variables[currentRow].initial = text
		# changing a property of a QTableWidgetItem requires removal of item, change of property and re-setting the item
		item = self.ui.tableWidget.takeItem(currentRow,4)
		item.setText(text)
		self.ui.tableWidget.setItem(currentRow,4,item)
		self.ui.tableWidget.resizeColumnToContents(4)

	
	@pyqtSlot(str)
	def on_comboBoxTypeID_currentIndexChanged(self, text):
		# get current row
		currentRow = self.ui.tableWidget.currentRow()
		assert(currentRow >= 0 and currentRow < len(self.variables))
		# update variable cache
		self.variables[currentRow].typeID = text
		# changing a property of a QTableWidgetItem requires removal of item, change of property and re-setting the item
		item = self.ui.tableWidget.takeItem(currentRow,5)
		item.setText(text)
		self.ui.tableWidget.setItem(currentRow,5,item)
		self.ui.tableWidget.resizeColumnToContents(5)

	
	@pyqtSlot(str)
	def on_lineEditStart_textEdited(self,text):
		# get current row
		currentRow = self.ui.tableWidget.currentRow()
		assert(currentRow >= 0 and currentRow < len(self.variables))
		# update variable cache
		self.variables[currentRow].startValue = text # conversion to suitable data type is checked later
		# changing a property of a QTableWidgetItem requires removal of item, change of property and re-setting the item
		item = self.ui.tableWidget.takeItem(currentRow,6)
		item.setText(text)
		self.ui.tableWidget.setItem(currentRow,6,item)
		self.ui.tableWidget.resizeColumnToContents(6)
