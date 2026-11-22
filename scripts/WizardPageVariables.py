#!/usr/bin/env python3

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


import os.path

from PyQt6.QtWidgets import QWidget, QTableWidgetItem, QButtonGroup
from PyQt6.QtCore import pyqtSlot, Qt
from PyQt6.QtGui import QFontMetrics, QIcon

from Ui_WizardPageVariables import Ui_WizardPageVariables

from FMIGenerator import FMIGenerator, VarDef, varDefFromJson


# *** FMI 2.0 rules for valid attribute combinations (FMI 2.0 standard, section 2.2.7) ***

# Variabilities allowed for each causality
VALID_VARIABILITY = {
	"parameter"           : ["fixed", "tunable"],
	"calculatedParameter" : ["fixed", "tunable"],
	"input"               : ["discrete", "continuous"],
	"output"              : ["constant", "discrete", "continuous"],
	"local"               : ["constant", "fixed", "tunable", "discrete", "continuous"],
	"independent"         : ["continuous"]
}

# Order in which a replacement variability is picked when the current one becomes invalid
VARIABILITY_PRIORITY = ["continuous", "discrete", "fixed", "tunable", "constant"]

# Causalities that must not have an 'initial' attribute
NO_INITIAL_CAUSALITIES = ["input", "independent"]

# Table column indexes
COL_NAME, COL_VALUEREF, COL_VARIABILITY, COL_CAUSALITY, COL_INITIAL, COL_TYPE, COL_START, COL_UNIT, COL_DESC = range(9)


def validVariabilities(causality, typeID):
	"""Returns the variabilities allowed for the given causality and type."""
	valid = VALID_VARIABILITY.get(causality, [])
	if typeID != "Real":
		valid = [v for v in valid if v != "continuous"]
	return valid


def validInitials(causality, variability):
	"""Returns the 'initial' values allowed for the given causality and variability
	(first entry is not necessarily the default, see defaultInitial())."""
	if causality in NO_INITIAL_CAUSALITIES:
		return []
	if variability == "constant":
		return ["exact"]
	if causality == "parameter":
		return ["exact"]
	if causality == "calculatedParameter":
		return ["approx", "calculated"]
	if causality == "local" and variability in ["fixed", "tunable"]:
		return ["approx", "calculated"]
	# output/local with discrete/continuous variability
	return ["exact", "approx", "calculated"]


def defaultInitial(causality, variability):
	"""Returns the FMI default for 'initial', or empty string if no initial attribute is allowed."""
	valid = validInitials(causality, variability)
	if len(valid) == 0:
		return ""
	if "calculated" in valid:
		return "calculated"
	return valid[0]


def displayedInitial(var):
	"""Returns the 'initial' value shown in the table (none for causalities without initial attribute)."""
	if var.causality in NO_INITIAL_CAUSALITIES:
		return ""
	return var.initial


# *** Tooltip texts ***
# Format "<b>Title</b><br><br>Body" is rendered as a card by TooltipPopup; a note "<br><br><i>...</i>"
# is appended for disabled options.

TOOLTIPS = {
	"variability" : {
		"constant"   : "<b>constant</b><br><br>The value never changes. It is fixed by the start value "
					   "in modelDescription.xml.",
		"fixed"      : "<b>fixed</b><br><br>The value is set or computed during initialization and does not "
					   "change afterwards.",
		"tunable"    : "<b>tunable</b><br><br>Like <i>fixed</i>, but the master may change the value between "
					   "simulation steps (outside of initialization). The model must then recompute "
					   "dependent quantities.",
		"discrete"   : "<b>discrete</b><br><br>The value changes only at events (time or state events) and is "
					   "constant in between. The only choice for Integer, Boolean and String variables "
					   "that change over time.",
		"continuous" : "<b>continuous</b><br><br>The value may change at any time during integration. "
					   "Only allowed for variables of type Real."
	},
	"causality" : {
		"parameter"           : "<b>parameter</b><br><br>Independent parameter set by the user or master "
								"before the simulation. A start value is required.",
		"calculatedParameter" : "<b>calculatedParameter</b><br><br>Parameter computed by the FMU during "
								"initialization from other parameters. It can be read by the master.",
		"input"               : "<b>input</b><br><br>Value provided by the master (e.g. from another FMU) "
								"during the simulation. The start value is used until the master sets a value.",
		"output"              : "<b>output</b><br><br>Value computed by the FMU and provided to the master, "
								"e.g. to connect it to inputs of other FMUs.",
		"local"               : "<b>local</b><br><br>Internal variable of the model. It is visible in "
								"modelDescription.xml (e.g. for output files) but not used for connections.",
		"independent"         : "<b>independent</b><br><br>The independent variable of the model, usually the "
								"simulation time. At most one variable may be independent; it must be a "
								"continuous Real without start value."
	},
	"initial" : {
		"exact"      : "<b>exact</b><br><br>The variable is initialized with its start value.",
		"approx"     : "<b>approx</b><br><br>The variable is computed during initialization; the start value "
					   "is only used as an initial guess for an iteration.",
		"calculated" : "<b>calculated</b><br><br>The variable is computed from other variables during "
					   "initialization. No start value is written."
	},
	"type" : {
		"Real"    : "<b>Real</b><br><br>Floating point value (C++ <tt>double</tt>). The only type that may "
					"have a unit and continuous variability.",
		"Integer" : "<b>Integer</b><br><br>Integer value (C++ <tt>int</tt>).",
		"Boolean" : "<b>Boolean</b><br><br>Boolean value (C++ <tt>bool</tt>, stored as <tt>fmi2Boolean</tt>).",
		"String"  : "<b>String</b><br><br>Text value (C++ <tt>std::string</tt>)."
	}
}


def toolTipText(group, option, note=""):
	"""Composes the tooltip text, optionally with a note (shown muted below a hairline)."""
	text = TOOLTIPS[group][option]
	if len(note) != 0:
		text += "<br><br><i>{}</i>".format(note)
	return text



class WizardPageVariables(QWidget):
	def __init__(self):
		super().__init__()
		self.ui = Ui_WizardPageVariables()
		self.ui.setupUi(self)

		# tool button icons (PyQt6 has no resource compiler, so load them from file)
		gfxDir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ui", "gfx")
		self.ui.toolButtonAdd.setIcon(QIcon(os.path.join(gfxDir, "plus.png")))
		self.ui.toolButtonRemove.setIcon(QIcon(os.path.join(gfxDir, "minus.png")))

		# radio buttons for each attribute, keyed by the FMI attribute value
		self.variabilityButtons = {
			"constant"   : self.ui.radioButtonVariabilityConstant,
			"fixed"      : self.ui.radioButtonVariabilityFixed,
			"tunable"    : self.ui.radioButtonVariabilityTunable,
			"discrete"   : self.ui.radioButtonVariabilityDiscrete,
			"continuous" : self.ui.radioButtonVariabilityContinuous
		}
		self.causalityButtons = {
			"parameter"           : self.ui.radioButtonCausalityParameter,
			"calculatedParameter" : self.ui.radioButtonCausalityCalculatedParameter,
			"input"               : self.ui.radioButtonCausalityInput,
			"output"              : self.ui.radioButtonCausalityOutput,
			"local"               : self.ui.radioButtonCausalityLocal,
			"independent"         : self.ui.radioButtonCausalityIndependent
		}
		self.initialButtons = {
			"exact"      : self.ui.radioButtonInitialExact,
			"approx"     : self.ui.radioButtonInitialApprox,
			"calculated" : self.ui.radioButtonInitialCalculated
		}
		self.typeButtons = {
			"Real"    : self.ui.radioButtonTypeReal,
			"Integer" : self.ui.radioButtonTypeInteger,
			"Boolean" : self.ui.radioButtonTypeBoolean,
			"String"  : self.ui.radioButtonTypeString
		}

		# All radio buttons share the same parent widget, so each attribute gets its own exclusive
		# button group. buttonClicked is only emitted for user interaction, not for setChecked().
		self.variabilityGroup = self.createButtonGroup(self.variabilityButtons, "variability", self.onVariabilityClicked)
		self.causalityGroup = self.createButtonGroup(self.causalityButtons, "causality", self.onCausalityClicked)
		self.initialGroup = self.createButtonGroup(self.initialButtons, "initial", self.onInitialClicked)
		self.typeGroup = self.createButtonGroup(self.typeButtons, "type", self.onTypeClicked)

		self.setEditFieldsEnabled(False) # disabled by default
		self.variables = []

		# add default variable
		newVar = VarDef("ResultRootDir", "fixed", "parameter", "exact", "String")
		newVar.valueRef = 42
		newVar.startValue = "" # start value is empty, this parameter is automatically supplied by MasterSim
		newVar.description = "A writeable directory generated for each slave of this FMU to store slave-specific output/data files."

		self.variables.append(newVar)

		self.updateTable()
		self.ui.tableWidget.selectRow(0)
		self.show()


	def createButtonGroup(self, buttons, tooltipGroup, slot):
		group = QButtonGroup(self)
		group.setExclusive(True)
		for option, btn in buttons.items():
			group.addButton(btn)
			btn.setToolTip(toolTipText(tooltipGroup, option))
		group.buttonClicked.connect(slot)
		return group


	def setEditFieldsEnabled(self, enabled):
		self.ui.groupBox_4.setEnabled(enabled)
		self.ui.groupBox_2.setEnabled(enabled)


	def currentVariable(self):
		currentRow = self.ui.tableWidget.currentRow()
		assert(currentRow >= 0 and currentRow < len(self.variables))
		return currentRow, self.variables[currentRow]


	def setTableCell(self, row, col, text):
		"""Updates the text of a table cell and resizes the column."""
		# changing a property of a QTableWidgetItem requires removal of item, change of property and re-setting the item
		item = self.ui.tableWidget.takeItem(row, col)
		item.setText(text)
		self.ui.tableWidget.setItem(row, col, item)
		self.ui.tableWidget.resizeColumnToContents(col)


	def updateTable(self):
		"""Syncronizes self.variables with table widget"""

		self.ui.tableWidget.setRowCount(len(self.variables))
		for i in range(len(self.variables)):
			var = self.variables[i]
			texts = [var.name, "{}".format(var.valueRef), var.variability, var.causality, displayedInitial(var),
					 var.typeID, "{}".format(var.startValue), var.unit, var.description]
			for col in range(len(texts)):
				item = QTableWidgetItem()
				item.setFlags( Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
				item.setText(texts[col])
				self.ui.tableWidget.setItem(i, col, item)

		self.ui.tableWidget.resizeColumnsToContents()
		self.ui.tableWidget.setAlternatingRowColors(True)
		f = QFontMetrics(self.ui.tableWidget.font())
		self.ui.tableWidget.verticalHeader().setDefaultSectionSize(f.lineSpacing())
		self.ui.tableWidget.setMinimumHeight(f.lineSpacing()*8)


	def updateEditField(self, var):
		"""Shows the properties of var in the edit fields. Does not modify var, even if its attribute
		combination is invalid (invalid options are only greyed out)."""
		self.setEditFieldsEnabled(True)

		self.ui.lineEditName.setText(var.name)
		self.ui.spinBoxValueRef.setValue(var.valueRef)
		self.checkButton(self.variabilityGroup, self.variabilityButtons, var.variability)
		self.checkButton(self.causalityGroup, self.causalityButtons, var.causality)
		self.checkButton(self.typeGroup, self.typeButtons, var.typeID)
		self.ui.lineEditUnit.setText( var.unit )
		self.ui.lineEditDescription.setText( var.description )
		self.ui.lineEditStart.setText( var.startValue )
		# initial radio buttons are set in updateOptionStates()
		self.updateOptionStates(var)


	def checkButton(self, group, buttons, option):
		"""Checks the radio button for option; unchecks all buttons if option is unknown/empty."""
		if option in buttons:
			buttons[option].setChecked(True)
		else:
			# an exclusive group does not allow unchecking the checked button
			group.setExclusive(False)
			for btn in buttons.values():
				btn.setChecked(False)
			group.setExclusive(True)


	def updateOptionStates(self, var):
		"""Greys out options that are invalid for the current variable definition and updates the
		tooltips with the reason."""

		# variability depends on causality and type
		validVar = validVariabilities(var.causality, var.typeID)
		for option, btn in self.variabilityButtons.items():
			note = ""
			if option not in validVar:
				if option == "continuous" and var.typeID != "Real" and option in VALID_VARIABILITY.get(var.causality, []):
					note = "Only available for type Real."
				else:
					note = "Not available with causality '{}'.".format(var.causality)
			btn.setEnabled(len(note) == 0)
			btn.setToolTip(toolTipText("variability", option, note))

		# causality: always selectable, but 'independent' needs a Real
		self.causalityButtons["independent"].setToolTip(toolTipText("causality", "independent",
			"" if var.typeID == "Real" else "Selecting it switches the type to Real."))

		# initial depends on causality and variability
		validInit = validInitials(var.causality, var.variability)
		for option, btn in self.initialButtons.items():
			note = ""
			if var.causality in NO_INITIAL_CAUSALITIES:
				note = "Variables with causality '{}' have no initial attribute.".format(var.causality)
			elif option not in validInit:
				note = "Not available with causality '{}' and variability '{}'.".format(var.causality, var.variability)
			btn.setEnabled(len(note) == 0)
			btn.setToolTip(toolTipText("initial", option, note))
		self.checkButton(self.initialGroup, self.initialButtons, displayedInitial(var))

		# type: 'continuous' is only possible for Real
		for option, btn in self.typeButtons.items():
			note = ""
			if option != "Real":
				if var.causality == "independent":
					note = "Selecting it switches the causality to 'local'."
				elif var.variability == "continuous":
					note = "Selecting it switches the variability to 'discrete'."
			btn.setToolTip(toolTipText("type", option, note))

		# unit only for Real
		isReal = var.typeID == "Real"
		self.ui.labelUnit.setEnabled(isReal)
		self.ui.lineEditUnit.setEnabled(isReal)

		# start value is not written for calculated variables and the independent variable
		hasStart = var.causality == "input" or \
			(var.causality != "independent" and var.initial != "calculated")
		self.ui.label_6.setEnabled(hasStart)
		self.ui.lineEditStart.setEnabled(hasStart)


	def applyVariableDefinition(self, row, var):
		"""Replaces invalid dependent attributes by FMI defaults (order: causality/type ->
		variability -> initial) and updates table and edit fields."""
		if var.typeID != "Real" and var.causality == "independent":
			var.causality = "local"
		validVar = validVariabilities(var.causality, var.typeID)
		if var.variability not in validVar:
			var.variability = [v for v in VARIABILITY_PRIORITY if v in validVar][0]
		validInit = validInitials(var.causality, var.variability)
		if len(validInit) != 0 and var.initial not in validInit:
			var.initial = defaultInitial(var.causality, var.variability)

		self.setTableCell(row, COL_VARIABILITY, var.variability)
		self.setTableCell(row, COL_CAUSALITY, var.causality)
		self.setTableCell(row, COL_INITIAL, displayedInitial(var))
		self.setTableCell(row, COL_TYPE, var.typeID)
		# sync radio buttons with possibly changed attributes
		self.checkButton(self.variabilityGroup, self.variabilityButtons, var.variability)
		self.checkButton(self.causalityGroup, self.causalityButtons, var.causality)
		self.checkButton(self.typeGroup, self.typeButtons, var.typeID)
		self.updateOptionStates(var)


	@staticmethod
	def optionOf(buttons, button):
		for option, btn in buttons.items():
			if btn is button:
				return option
		assert(False)


	def onVariabilityClicked(self, button):
		row, var = self.currentVariable()
		var.variability = self.optionOf(self.variabilityButtons, button)
		self.applyVariableDefinition(row, var)


	def onCausalityClicked(self, button):
		row, var = self.currentVariable()
		var.causality = self.optionOf(self.causalityButtons, button)
		if var.causality == "independent":
			var.typeID = "Real"
		self.applyVariableDefinition(row, var)


	def onInitialClicked(self, button):
		row, var = self.currentVariable()
		var.initial = self.optionOf(self.initialButtons, button)
		self.applyVariableDefinition(row, var)


	def onTypeClicked(self, button):
		row, var = self.currentVariable()
		var.typeID = self.optionOf(self.typeButtons, button)
		self.applyVariableDefinition(row, var)


	@pyqtSlot(str)
	def onLoadDefaults(self, inputDataFile):
		fmiGenerator = FMIGenerator()
		fmiGenerator.readInputData(inputDataFile)
		self.variables = fmiGenerator.variables
		self.updateTable()
		if len(self.variables) > 0:
			self.ui.tableWidget.selectRow(0)
			self.updateEditField(self.variables[0])
		else:
			self.setEditFieldsEnabled(False)


	@pyqtSlot()
	def on_toolButtonAdd_clicked(self):
		# add a new table row and enabled edit field
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
			self.setEditFieldsEnabled(False)
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
		row, var = self.currentVariable()
		var.name = text.strip()
		self.setTableCell(row, COL_NAME, text)


	@pyqtSlot(str)
	def on_lineEditDescription_textEdited(self,text):
		row, var = self.currentVariable()
		var.description = text
		self.setTableCell(row, COL_DESC, text)


	@pyqtSlot(int)
	def on_spinBoxValueRef_valueChanged(self, value):
		row, var = self.currentVariable()
		var.valueRef = value
		self.setTableCell(row, COL_VALUEREF, "{}".format(value))


	@pyqtSlot(str)
	def on_lineEditStart_textEdited(self,text):
		row, var = self.currentVariable()
		var.startValue = text # conversion to suitable data type is checked later
		self.setTableCell(row, COL_START, text)


	@pyqtSlot(str)
	def on_lineEditUnit_textEdited(self,text):
		row, var = self.currentVariable()
		var.unit = text
		self.setTableCell(row, COL_UNIT, text)
