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
import json
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

	def toJson(self):
		return {
		    "name" : self.name,
		    "valueRef" : self.valueRef,
		    "variability" : self.variability,
		    "causality" : self.causality,
		    "initial" : self.initial,
		    "typeID" : self.typeID,
		    "startValue" : self.startValue
		}

def varDefFromJson(data):
	v = VarDef(data['name'], data['variability'], data['causality'], data['initial'], data['typeID'])
	v.startValue = data['startValue']
	v.valueRef = data['valueRef']
	return v

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
		self.messages = []
		
		self.autobuild = True


	def printMsg(self, text):
		print(text)
		self.messages.append(text)
		

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

		self.printMsg("Target directory   : {}".format(self.targetDirPath))

		# the source directory with the template files is located relative to
		# this python script: ../data/FMIProject

		# get the path of the current python script
		scriptpath = os.path.abspath(os.path.dirname(sys.argv[0]))
		self.printMsg("Script path        : {}".format(scriptpath))

		# relative path (from script file) to resource/template directory
		templateDirPath = os.path.join(scriptpath, "../data/" + TEMPLATE_FOLDER_NAME)
		templateDirPath = os.path.abspath(templateDirPath)
		self.printMsg("Template location  : {}".format(templateDirPath))

		# user may have specified "FMI_template" as model name 
		# (which would be weird and break the code, hence a warning)
		if self.modelName == "FMI_template":
			printMsg("WARNING: model name is same as template folder name. This may not work!")
		
		# store input data into <targetDir>/<modelName>.input so that it can be read again by wizard to
		# populate input data
		self.writeInputData(self.targetDirPath + ".input")
		
		self.printMsg("Copying template directory to target directory (and renaming files)")
		self.copyTemplateDirectory(templateDirPath)
		
		self.printMsg("Generating unique value references")
		# first create a set of all predefined valueReferences
		valueRefs = set()
		for var in self.variables:
			if var.valueRef != -1:
				valueRefs.add(var.valueRef)
		# start auto-numbering from valueRef 1 
		nextValueRef = 1
		for var in self.variables:
			# generate value if auto-numbered
			if var.valueRef == -1:
				# find first unused index
				i = nextValueRef
				while i in valueRefs:
					i = i + 1
				nextValueRef = i
				valueRefs.add(i) # add value ref to set of already used valueRefs
				var.valueRef = nextValueRef # remember assigned value reference
	
		self.printMsg ("Adjusting template files (replacing placeholders)")
		self.substitutePlaceholders()

		if self.autobuild:
			self.printMsg("Test-building FMU")
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
				
			# if parent directory does not yet exist, create it
			parentDir = os.path.dirname(self.targetDirPath)
			if not os.path.exists(parentDir):
				os.makedirs(parentDir)
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
					if sys.version_info[0] < 3:
						fobj = open(src, 'r')
						data = fobj.read().decode('utf8')
					else:
						fobj = open(src, 'r', encoding='utf-8')
						data = fobj.read()
					fobj.close()
				except Exception as e:
					self.printMsg(str(e))
					raise RuntimeError("Error reading file: {}".format(src))
	
				# generic data adjustment
				data = data.replace(TEMPLATE_FOLDER_NAME, self.modelName)

				# special handling for certain file types
				
				# 1. modelDescription.xml
				if f == "modelDescription.xml":
					data = self.adjustModelDescription(data, localTime, guid)
			
				# 2. <modelName>.cpp
				if f==self.modelName + ".cpp":
					data = self.adjustSourceCodeFiles(data, guid)
	
				# finally, write data back to file
				try:
					if sys.version_info[0] < 3:
						fobj = open(src, 'w')
						fobj.write(data.encode("utf8"))
					else:
						fobj = open(src, 'w',encoding="utf-8")
						fobj.write(data)
					fobj.close()
				except Exception as e:
					self.printMsg("Error writing file: {}".format(str(e)))
					raise RuntimeError("Error writing file: {}".format(src))


	def adjustModelDescription(self, data, localTimeStamp, guid):
		"""Adjusts content of `modelDescription.xml` file.
		Take the content of template file in argument data. Inserts strings for model name, description, 
		date and time, GUID, ...

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
		
		# TODO : substitute remaining placeholders
		data = data.replace("$$version$$","1.0.0")
		data = data.replace("$$author$$","not specified")
		data = data.replace("$$copyright$$","not specified")
		data = data.replace("$$license$$","not specified")
		
		
		# generate scalar variable section
		
		VARIABLE_TEMPLATE = """
		<!-- Index of variable = "$$index$$" -->
		<ScalarVariable
			name="$$name$$"
			valueReference="$$valueRef$$"
			variability="$$variability$$"
			causality="$$causality$$"
			initial="$$initial$$">
			<$$typeID$$$$start$$/>
		</ScalarVariable>		
		"""
		
		MODEL_STRUCTURE_TEMPLATE = """			<Unknown index="$$index$$" dependencies="$$dependlist$$"/>
		"""
		
		scalarVariableDefs = ""
		# now add all variables one by one
		idx = 0
		dependList = ""
		for var in self.variables:
			idx = idx + 1
			var.idx = idx
			varDefBlock = VARIABLE_TEMPLATE
			varDefBlock = varDefBlock.replace("$$index$$",str(idx))
			varDefBlock = varDefBlock.replace("$$name$$",var.name)
			
			# generate value if auto-numbered
			assert(var.valueRef != -1)
			varDefBlock = varDefBlock.replace("$$valueRef$$",str(var.valueRef))	
			
			if var.causality == "input":
				dependList = dependList + " " + str(idx)
			
			varDefBlock = varDefBlock.replace("$$variability$$",var.variability)
			varDefBlock = varDefBlock.replace("$$causality$$",var.causality)
			varDefBlock = varDefBlock.replace("$$initial$$",var.initial)

			varDefBlock = varDefBlock.replace("$$typeID$$",var.typeID)
			
			if var.initial=="calculated":
				varDefBlock = varDefBlock.replace("$$start$$","")
			else:
				varDefBlock = varDefBlock.replace("$$start$$",' start="{}"'.format(var.startValue))
		
			scalarVariableDefs = scalarVariableDefs + "\n" + varDefBlock
		
		data = data.replace("$$scalarVariables$$",scalarVariableDefs)

		dependList = dependList.strip()
		
		# output dependency block	
		modelStructureDefs = ""
		for var in self.variables:
			if var.causality == "output":
				dependsDef = MODEL_STRUCTURE_TEMPLATE
				dependsDef = dependsDef.replace("$$index$$",str(var.idx))
				dependsDef = dependsDef.replace("$$dependlist$$", dependList)
				modelStructureDefs = modelStructureDefs + "\n" + dependsDef
	
		data = data.replace("$$outputDependencies$$", modelStructureDefs)
		return data


	def adjustSourceCodeFiles(self, data, guid):
		"""Adjusts content of `<modelName>.cpp` file.
		Replaces the following placeholders:
		
		- $$variables$$ - defines for each published variables
		- $$initialization$$ - start values for all input and output variables
		- $$initialStatesME$$ - initialization code for Model Exchange
		- $$initialStatesCS$$ - initialization code for Model Exchange
		- $$getInputVars$$ - retrieves input/parameter values for access in C++ code
		- $$setOutputVars$$ - sets calculated values for access in C++ code
		
		Arguments:

		data -- string holding the contents of the <modelName>.cpp file
		guid -- globally unique identifier

		Returns:
		
		Returns the modified string.
		
		"""
		
		data = data.replace("$$GUID$$", str(guid))		

		# generate variable defines
		s = ""
		for var in self.variables:
			# compose type prefix for cpp member variables
			typePrefix = ""
			cppType = ""
			if var.typeID == "Real":
				typePrefix = "real"
				cppType = "double"
			elif  var.typeID == "Boolean":
				typePrefix = "bool"
				cppType = "bool"
			elif  var.typeID == "Integer":
				typePrefix = "integer"
				cppType = "int"
			elif  var.typeID == "String":
				typePrefix = "string"
				cppType = "const std::string &"
			assert(typePrefix)
			
			if var.causality == "input":
				sdef = "#define FMI_INPUT_{} {}".format(var.name, var.valueRef)
				s = s + sdef + "\n"
				var.varDefine = "FMI_INPUT_{}".format(var.name)
				var.cppVariable = "m_{}Var[{}]".format(typePrefix, var.varDefine)
				var.getStatement = "{} {} = {};".format(cppType, var.name, var.cppVariable)
			elif var.causality == "output":
				sdef = "#define FMI_OUTPUT_{} {}".format(var.name, var.valueRef)
				s = s + sdef + "\n"
				var.varDefine = "FMI_OUTPUT_{}".format(var.name)
				var.cppVariable = "m_{}Var[{}]".format(typePrefix, var.varDefine)
				if var.typeID == "String":
					var.setStatement = '{} = ""; // TODO : store your results here'.format(var.cppVariable)
				else:
					var.setStatement = "{} = 0; // TODO : store your results here".format(var.cppVariable)
			elif var.causality == "parameter":
				sdef = "#define FMI_PARA_{} {}".format(var.name, var.valueRef)
				s = s + sdef + "\n"
				var.varDefine = "FMI_PARA_{}".format(var.name)
				var.cppVariable = "m_{}Var[{}]".format(typePrefix, var.varDefine)
				var.getStatement = "{} {} = {};".format(cppType, var.name, var.cppVariable)
			else:
				var.varDefine = "" # variable will not be used in cpp code
				

		data = data.replace("$$variables$$", s)
		
		# generate initialization code
		sIn = ""
		for var in self.variables:
			if var.causality == "input" or var.causality == "parameter":
				if var.typeID == "String":
					sdef = '\t{} = \"{}\";'.format(var.cppVariable, var.startValue)
				else:
					# we expect start value to be an integer value, otherwise we default to 0
					if len(var.startValue) == 0:
						var.startValue = "0"
					sdef = "\t{} = {};".format(var.cppVariable, var.startValue)
				sIn = sIn + sdef + "\n"
		if len(sIn) > 0:
			sIn = "\t// initialize input variables and/or parameters\n" + sIn + "\n"
			
		sOut = ""
		for var in self.variables:
			if var.causality == "output":
				if var.typeID == "String":
					sdef = '\t\t{} = \"{}\";'.format(var.cppVariable, var.startValue)
				else:
					# we expect start value to be an integer value, otherwise we default to 0
					if len(var.startValue) == 0:
						var.startValue = "0"
					sdef = "\t{} = {};".format(var.cppVariable, var.startValue)
				sOut = sOut + sdef + "\n"
		if len(sOut) > 0:
			sOut = "\t// initialize output variables\n" + sOut + "\n"
		
		data = data.replace("$$initialization$$", sIn + sOut)		
		
		# todo states
		
		data = data.replace("$$initialStatesME$$", "")		
		data = data.replace("$$initialStatesCS$$", "")		
		
		# compose getter block
		s = ""
		for var in self.variables:
			if var.causality == "input" or var.causality == "parameter":
				sdef = "\t" + var.getStatement
				s = s + sdef + "\n"		
		data = data.replace("$$getInputVars$$", s)
		
		# compose setter block
		s = ""
		for var in self.variables:
			if var.causality == "output":
				sdef = "\t" + var.setStatement
				s = s + sdef + "\n"
		data = data.replace("$$setOutputVars$$", s)		
		
		return data
	
	
	def testBuildFMU(self):
		"""Runs a cmake-based compilation of the generated FMU to check if the code compiles.
		"""
		
		# generate path to /build subdir
		buildDir = os.path.join(self.targetDirPath, "build")
		binDir = os.path.join(self.targetDirPath, "bin/release")
	
		self.printMsg("We are now test-building the FMU. You should first implement your FMU functionality and afterwards "
		      "build and deploy the FMU!")
		try:

			# Different script handling based on platform
			if platform.system() == "Windows":
				
				# call batch file to build the FMI library
				pipe = subprocess.Popen(["build_VC_x64.bat"], shell=True, creationflags=subprocess.CREATE_NEW_CONSOLE, cwd = buildDir, stdout = subprocess.PIPE, stderr = subprocess.PIPE)                
				# retrieve output and error messages
				outputMsg, errorMsg = pipe.communicate()
				# get return code
				rc = pipe.returncode
	
				# if return code is different from 0, print the error message
				if rc != 0:
					self.printMsg(str(outputMsg) + "\n" + str(errorMsg))
					raise RuntimeError("Error during compilation of FMU.")

				self.printMsg("Compiled FMU successfully")
		
				# call batch file to build the FMI library
				pipe = subprocess.Popen(["deploy.bat"], shell=True, creationflags=subprocess.CREATE_NEW_CONSOLE, cwd = buildDir, stdout = subprocess.PIPE, stderr = subprocess.PIPE)                
				# retrieve output and error messages
				outputMsg, errorMsg = pipe.communicate()
				# get return code
				rc = pipe.returncode
	
				if rc != 0:
					self.printMsg(str(outputMsg) + "\n" + str(errorMsg))
					raise RuntimeError("Error during compilation of FMU")

				self.printMsg("Successfully created {}".format(self.modelName + ".fmu")	)
	
			else:
				# shell file execution for Mac & Linux
				pipe = subprocess.Popen(["bash", './build.sh'], cwd = buildDir, stdout = subprocess.PIPE, stderr = subprocess.PIPE)                           
				outputMsg,errorMsg = pipe.communicate()  
				rc = pipe.returncode             
	
				if rc != 0:
					self.printMsg(errorMsg)
					raise RuntimeError("Error during compilation of FMU")

				self.printMsg("Compiled FMU successfully")
	
				# Deployment
	
				# shell file execution for Mac & Linux
				deploy = subprocess.Popen(["bash", './deploy.sh'], cwd = buildDir, stdout = subprocess.PIPE, stderr = subprocess.PIPE)                           
				outputMsg,errorMsg = deploy.communicate()  
				dc = deploy.returncode             
	
				if dc != 0:
					self.printMsg(errorMsg)
					raise RuntimeError("Error during assembly of FMU")

				self.printMsg("Successfully created {}".format(self.modelName + ".fmu")	)
	
		except Exception as e:
			self.printMsg(str(e))
			self.printMsg("Error building FMU.")
			raise


	def writeInputData(self, targetFile):
		"""Writes all input data to FMIGenerator to file so it can be read later by the FMIGeneratorWizard to 
		populate the dialog again (greatly helps in testing the code)"""
		
		varArray = []
		
		for v in self.variables:
			varArray.append(v.toJson())
		
		data = {
		  "modelName" : self.modelName,
		  "description" : self.description,
		  "variables" : varArray
		}
		
		# if parent directory does not yet exist, create it
		parentDir = os.path.dirname(targetFile)
		parentDir = os.path.abspath(parentDir)
		if not os.path.exists(parentDir):
			os.makedirs(parentDir)

		with open(targetFile, 'w') as outfile:
			json.dump(data, outfile, indent=4)		
			
	
	def readInputData(self, targetFile):
		with open(targetFile, 'r') as f:
			data = json.load(f)
			self.description = data['description']
			for a in data['variables']:
				v = varDefFromJson(a)
				self.variables.append(v)
