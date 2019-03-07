# -*- coding: utf-8 -*-
# Implementation of class FMIGenerator
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

import os
import sys
import shutil
from shutil import *
import uuid
import time
import subprocess
import datetime
import platform
from third_party.send2trash_master.send2trash import send2trash

# The directory name of the template folder
TEMPLATE_FOLDER_NAME = "FMI_template"

class VarDef:
	"""Contains all properties of a scalar variable in the model description."""
	def __init__(self):
		self.name = ""
		self.valueRef = -1 # means automatic enumeration of value references
		self.variability = "" # constant, fixed, tunable, discrete, continuous
		self.causality = "" # parameter, calculatedParameter, input, output, local, independent
		self.initial = "" # exact, approx, calculated
		self.typeID = "" # Real, Integer, Boolean, String
		self.startValue = ""

	def __init__(self, name, variability, causality, initial, typeID):
		self.name = name
		self.valueRef = -1
		self.variability = variability
		self.causality = causality
		self.initial = initial
		self.typeID = typeID
		self.startValue = ""



class FMIGenerator:
	"""Class that encapsulates all parameters needed to generate the FMU.

	Usage: create class instance, set member variables, call function generate()
	"""

	def __init__(self):
		""" Constructor, initializes member variables.

		Member variables:
		
		targetDir -- Target directory can be relative (to current working directory) or
					 absolute. FMU directory is created below this directory, for example:
					    <target path>/<modelName>/
					 By default, target path is empty which means that the subdirectory <modelName>
					 is created directly below the current working directory.
		modelName -- A user defined model name
		description -- A user defined description
		variables -- vector of type VarDefs with variable definitions (inputs, outputs, parameters) 
		"""
		self.targetDir = ""
		
		self.modelName = ""
		self.description = ""
		self.variables = []

	def generate(self):

		""" Main FMU generation function. Requires member variables to be set correctly.

		Functionality: first a template folder structure is copied to the target location. Then,
		placeholders in the original files are substituted.
		
		Target directory is generated using targetDir member variable, for relative directory, 
		the target directory is created from `<current working directory>/<targetDir>/<modelName>`.
		For absolute file paths the target directory is `<targetDir>/<modelName>`.
        """

		# sanity checks
		if self.modelName == "":
			raise RuntimeError("Missing model name")

		# compose target directory: check if self.targetPath is an absolute file path
		if (os.path.isabs(self.targetDir)):
			self.targetDirPath = os.path.join(self.targetDir, self.modelName)
		else:
			self.targetDirPath = os.path.join(os.getcwd(), self.targetDir)
			self.targetDirPath = os.path.join(self.targetDirPath, self.modelName)

		print("Target directory   : {}".format(self.targetDirPath))

		# the source directory with the template files is located relative to
		# this python script: ../data/FMIProject

		# get the path of the current python script
		scriptpath = os.path.abspath(os.path.dirname(sys.argv[0]))
		print("Script path        : {}".format(scriptpath))

		# relative path (from script file) to resource/template directory
		templateDirPath = os.path.join(scriptpath, "../data/" + TEMPLATE_FOLDER_NAME)
		templateDirPath = os.path.abspath(templateDirPath)
		print("Template location  : {}".format(templateDirPath))

		# user may have specified "FMI_template" as model name 
		# (which would be weird and break the code, hence a warning)
		if self.modelName == "FMI_template":
			print("WARNING: model name is same as template folder name. This may not work!")
			
		print("Copying template directory to target directory (and renaming files)")
		self.copyTemplateDirectory(templateDirPath)
		
		print ("Adjusting template files (replacing placeholders)")
		self.substitutePlaceholders()

		print ("Test-building FMU")
		self.testBuildFMU()
		
		# *** Done with FMU generation ***



	def copyTemplateDirectory(self, templatePath):
		"""Copies the template folder to the new location. Replaces the old name of directories, files 
		and script in the files with the newly user defined name (i.e.modelName).
		
		Path to target directory is stored in self.targetDirPath.
		If target directory exists already, it is moved to trash first.

		Const-function, does not modify the state of the object.

		Arguments:

		templatePath -- The absolute path to the template directory.
		
		Example::
		
		   self.copyTemplateDirectory("../data/FMI_template")
		   # will rename "FMI_template" to "testFMU" after copying
		"""

		try:
			# check if target directory exists already
			if os.path.exists(self.targetDirPath):
				# Move folder to thrash
				send2trash(self.targetDirPath)
				
			# Copy source folder to a new location(i.e. self.targetDirPath)
			shutil.copytree(templatePath, self.targetDirPath)
			# Set modified time of newly created folder
			os.utime(self.targetDirPath, None)
		except:
			raise RuntimeError("Cannot copy template directory to target directory")

		try:
			# rename files that must be named according as the modelName
			os.rename(self.targetDirPath + "/projects/Qt/" + TEMPLATE_FOLDER_NAME + ".pro", 
			          self.targetDirPath + "/projects/Qt/" + self.modelName + ".pro")
			os.rename(self.targetDirPath + "/src/" + TEMPLATE_FOLDER_NAME + ".cpp", 
			          self.targetDirPath + "/src/" + self.modelName + ".cpp")
			os.rename(self.targetDirPath + "/src/" + TEMPLATE_FOLDER_NAME + ".h", 
			          self.targetDirPath + "/src/" + self.modelName + ".h")
		except:
			raise RuntimeError("Cannot rename template files")


	def substitutePlaceholders(self):  
		"""Processes all template files and replaces placeholders within the files with generated values.
		
		1. It generates a globally unique identifier.
		2. It generates a local time stamp.
		3. It replaces placeholders.

		"""

		# Generate globally unique identifier
		guid = uuid.uuid1()

		# Generate time stamp of local date and time
		localTime = time.strftime('%Y-%m-%dT%I:%M:%SZ',time.localtime())

		# We process file after file
		
		# loop to walk through the new folder  
		for root, dirs, files in os.walk(self.targetDirPath):
			# process all files
			for f in files:
	
				# compose full file path
				src = os.path.join(root, f)
	
				try:
					# read file into memory, variable 'data'
					fobj = open(src, 'r')
					data = fobj.read()
					fobj.close()
				except:
					raise RuntimeError("Error reading file: {}".format(src))
	
				# generic data adjustment
				data = data.replace(TEMPLATE_FOLDER_NAME, self.modelName)

				# special handling for certain file types
				
				# 1. modelDescription.xml
				if f == "modelDescription.xml":
					data = self.adjustModelDescription(data, localTime, guid)
			
				# 2. <modelName>.cpp
				if f==self.modelName + ".cpp":
					data = data.replace("$$GUID$$", str(guid))
	
				# finally, write data back to file
				try:
					fobj = open(src, 'w')
					fobj.write(data)
					fobj.close()
				except:
					raise RuntimeError("Error writing file: {}".format(src))


	def adjustModelDescription(self, data, localTimeStamp, guid):
		"""Adjusts content of `modelDescription.xml` file.
		Reads the template file. Inserts strings for model name, description, 
		date and time, GUID, ...
		And writes the modified string to file again.

		Arguments:

		data -- string holding the contents of the modelDescription.xml file
		localTimeStamp -- time stamp of local time
		guid -- globally unique identifier

		Returns:
		
		Returns string with modified modelDescription.xml file
		"""

		data = data.replace("$$dateandtime$$",localTimeStamp)
		data = data.replace("$$GUID$$", str(guid))        
		data = data.replace("$$description$$", self.description)
		data = data.replace("$$modelName$$",self.modelName)
		
		return data



	def testBuildFMU(self):
		"""Runs a cmake-based compilation of the generated FMU to check if the code compiles.
		"""
		
		# generate path to /build subdir
		buildDir = os.path.join(self.targetDirPath, "build")
		binDir = os.path.join(self.targetDirPath, "bin/release")
	
		print("We are now test-building the FMU. You should first implement your FMU functionality and afterwards "
		      "build and deploy the FMU!")
		try:

			# Different script handling based on platform
			if platform.system() == "Windows":
				
				# call batch file to build the FMI library
				pipe = subprocess.Popen("build.bat", creationflags=subprocess.CREATE_NEW_CONSOLE, cwd = buildDir, stdout = subprocess.PIPE, stderr = subprocess.PIPE)                
				# retrieve output and error messages
				outputMsg, errorMsg = pipe.communicate()  
				# get return code
				rc = pipe.returncode 
	
				# if return code is different from 0, print the error message
				if rc != 0:
					print errorMsg
					raise RuntimeError("Error during compilation of FMU.")

				print "Compiled FMU successfully"
	
				# renaming/moving file    
				for root, dircs, files in os.walk(binDir):
					for file in files:
						if file == 'lib'+ self.modelName + '.so.1.0.0':
							oldFileName = os.path.join(binDir,'lib'+ self.modelName + '.so.1.0.0')
							newFileName = os.path.join(binDir,self.modelName + '.dll')
							os.rename(oldFileName,newFileName)
	
				deploy = subprocess.Popen(["bash", './deploy.sh'], cwd = buildDir, stdout = subprocess.PIPE, stderr = subprocess.PIPE)                           
				outputMsg,errorMsg = deploy.communicate()  
				dc = deploy.returncode             
	
				if dc != 0:
					print errorMsg
					raise RuntimeError("Error during compilation of FMU")

				print "Compiled FMU successfully"	                 
	
			else:
				# shell file execution for Mac & Linux
				pipe = subprocess.Popen(["bash", './build.sh'], cwd = buildDir, stdout = subprocess.PIPE, stderr = subprocess.PIPE)                           
				outputMsg,errorMsg = pipe.communicate()  
				rc = pipe.returncode             
	
				if rc != 0:
					print errorMsg
					raise RuntimeError("Error during compilation of FMU")

				print "Compiled FMU successfully"
	
				if platform.system() == 'Darwin':
					libName = "lib" + self.modelName + ".dylib.1.0.0"
				else:
					libName = "lib" + self.modelName + ".so.1.0.0"
					
				for root, dircs, files in os.walk(buildDir):
					for f in files:
						if f == libName:
							oldFileName = os.path.join(root, libName)
							newFileName = os.path.join(binDir, self.modelName + '.so')
							os.rename(oldFileName, newFileName)
							print ("Creating: {}".format(newFileName))
							break
	
				# Deployment
	
				# shell file execution for Mac & Linux
				deploy = subprocess.Popen(["bash", './deploy.sh'], cwd = buildDir, stdout = subprocess.PIPE, stderr = subprocess.PIPE)                           
				outputMsg,errorMsg = deploy.communicate()  
				dc = deploy.returncode             
	
				if dc != 0:
					print errorMsg
					raise RuntimeError("Error during assembly of FMU")

				print ("Successfully created {}".format(self.modelName + ".fmu")	)
	
		except Exception as e:
			print ("Error building FMU.")
			raise

