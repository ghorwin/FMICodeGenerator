#!/usr/bin/env python3

# Implementation of the project selection wizard page (create new or open existing FMU project).
#
#
# This file is part of FMICodeGenerator (https://github.com/ghorwin/FMICodeGenerator)
#
# BSD 3-Clause License
#
# Copyright (c) 2018, Andreas Nicolai
# All rights reserved.
#
# see https://github.com/ghorwin/FMICodeGenerator/blob/master/LICENSE for details.

import os

from PyQt6.QtWidgets import QWidget, QFileDialog, QListWidgetItem
from PyQt6.QtCore import pyqtSlot, pyqtSignal, QDir, QSettings, Qt

from Ui_WizardPageProject import Ui_WizardPageProject

# settings key holding the list of recently generated/updated FMU project directories
RECENT_PROJECTS_KEY = "RecentProjects"
MAX_RECENT_PROJECTS = 10


def appSettings():
	return QSettings("BKDS", "FmiCodeGenerator")


def recentProjects():
	"""Returns the list of recently generated/updated project directories (most recent first)."""
	value = appSettings().value(RECENT_PROJECTS_KEY, [])
	if value is None:
		return []
	if isinstance(value, str): # QSettings may return a single entry as plain string
		value = [value]
	return [str(v) for v in value if v]


def addRecentProject(projectDir):
	"""Puts the project directory at the top of the recent projects list (max. 10 entries)."""
	projectDir = os.path.normpath(os.path.abspath(projectDir))
	projects = [p for p in recentProjects() if os.path.normpath(p) != projectDir]
	projects.insert(0, projectDir)
	appSettings().setValue(RECENT_PROJECTS_KEY, projects[:MAX_RECENT_PROJECTS])


class WizardPageProject(QWidget):
	# emitted when a recent project is double-clicked (wizard proceeds to next page)
	recentProjectActivated = pyqtSignal()

	def __init__(self):
		super().__init__()
		self.ui = Ui_WizardPageProject()
		self.ui.setupUi(self)
		self.populateRecentProjects()
		self.updateEnabledState()
		self.show()


	def openExisting(self):
		return self.ui.radioButtonOpen.isChecked()


	def updateEnabledState(self):
		enabled = self.openExisting()
		self.ui.labelProjectDir.setEnabled(enabled)
		self.ui.lineEditProjectDir.setEnabled(enabled)
		self.ui.toolButtonBrowseProject.setEnabled(enabled)
		self.ui.labelRecentProjects.setEnabled(enabled)
		self.ui.listWidgetRecentProjects.setEnabled(enabled)
		self.ui.labelInfo.setEnabled(enabled)


	def populateRecentProjects(self):
		"""Fills the list widget with recent project directories that still exist."""
		self.ui.listWidgetRecentProjects.clear()
		for projectDir in recentProjects():
			if not os.path.isdir(projectDir):
				continue
			item = QListWidgetItem(projectDir)
			item.setData(Qt.ItemDataRole.UserRole, projectDir)
			item.setToolTip(projectDir)
			self.ui.listWidgetRecentProjects.addItem(item)
		hasItems = self.ui.listWidgetRecentProjects.count() > 0
		self.ui.labelRecentProjects.setVisible(hasItems)
		self.ui.listWidgetRecentProjects.setVisible(hasItems)


	@pyqtSlot(QListWidgetItem)
	def on_listWidgetRecentProjects_itemClicked(self, item):
		self.ui.lineEditProjectDir.setText(item.data(Qt.ItemDataRole.UserRole))


	@pyqtSlot(QListWidgetItem)
	def on_listWidgetRecentProjects_itemDoubleClicked(self, item):
		self.ui.lineEditProjectDir.setText(item.data(Qt.ItemDataRole.UserRole))
		self.recentProjectActivated.emit()


	@pyqtSlot(bool)
	def on_radioButtonOpen_toggled(self, checked):
		self.updateEnabledState()


	@pyqtSlot()
	def on_toolButtonBrowseProject_clicked(self):
		options = (QFileDialog.Option.DontUseNativeDialog | QFileDialog.Option.ShowDirsOnly |
				   QFileDialog.Option.DontResolveSymlinks)

		startDir = self.ui.lineEditProjectDir.text().strip()
		if not startDir:
			startDir = QDir.home().absolutePath()
		projectDir = QFileDialog.getExistingDirectory(self, "Select existing FMU project directory", startDir,
													  options=options)
		if projectDir:
			self.ui.lineEditProjectDir.setText(projectDir)
