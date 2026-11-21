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
import glob
import shutil
import uuid
import json
import subprocess
import datetime
import platform
from send2trash import send2trash

# The directory name of the template folder
TEMPLATE_FOLDER_NAME = "FMI_template"

# Suffix of the generated source files (<modelName>_generated.h/.cpp), which are
# overwritten on each project update.
GENERATED_FILE_SUFFIX = "_generated"

# Name of the backup directory inside a project, in which files are stored before they are overwritten
# during a project update.
BACKUP_DIR_NAME = ".backup"

class VarDef:
	"""Contains all properties of a scalar variable in the model description."""
	def __init__(self, name, variability, causality, initial, typeID):
		self.name = name
		self.valueRef = -1
		self.variability = variability
		self.causality = causality
		self.initial = initial
		self.typeID = typeID
		self.description = "" # an optional description of the variable's meaning
		self.unit = "" # the unit, only for Real-type variables
		self.startValue = ""

	def toJson(self):
		return {
			"name" : self.name,
			"valueRef" : self.valueRef,
			"variability" : self.variability,
			"causality" : self.causality,
			"initial" : self.initial,
			"typeID" : self.typeID,
			"startValue" : self.startValue,
			"description" : self.description,
			"unit" : self.unit
		}

def varDefFromJson(data):
	v = VarDef(data['name'], data['variability'], data['causality'], data['initial'], data['typeID'])
	if 'unit' in data:
		v.unit = data['unit']
	if 'description' in data:
		v.description = data['description']
	v.startValue = data['startValue']
	v.valueRef = data['valueRef']
	return v


def findProjectInputFile(projectDir):
	"""Looks for the project's .input file for a given FMU project directory.

	Search order:

	1. `<projectDir>/<dirname>.input`
	2. the only `*.input` file in `<projectDir>`
	3. legacy location `<projectDir>/../<dirname>.input` (projects created with FMICodeGenerator <= 1.3)

	Returns the path to the input file, or None if no file was found (or if the choice is ambiguous).
	"""
	projectDir = os.path.abspath(projectDir)
	dirName = os.path.basename(projectDir)
	candidate = os.path.join(projectDir, dirName + ".input")
	if os.path.isfile(candidate):
		return candidate
	inputFiles = glob.glob(os.path.join(projectDir, "*.input"))
	if len(inputFiles) == 1:
		return inputFiles[0]
	if len(inputFiles) > 1:
		return None
	candidate = os.path.join(os.path.dirname(projectDir), dirName + ".input")
	if os.path.isfile(candidate):
		return candidate
	return None


class FMIGenerator:
	"""Class that encapsulates all parameters needed to generate the FMU.

	Usage: create class instance, set member variables, call function generate() to create a new
	FMU project, or update() to update an existing FMU project.
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
		numberOfContinuousStates -- number of continuous states in the model (only exposed for ModelExchange functionality)
		overwrite -- if True, generate() moves an existing target directory to the trash; otherwise
					 generate() refuses to overwrite an existing directory
		"""
		self.targetDir = ""

		self.modelName = ""
		self.description = ""
		self.variables = []
		self.messages = []
		self.numberOfContinuousStates = 0

		self.autobuild = True
		self.overwrite = False


	def printMsg(self, text):
		print(text)
		self.messages.append(text)


	def templateDirPath(self):
		"""Returns the absolute path to the template directory (located relative to this script: ../data/FMI_template)."""
		scriptpath = os.path.dirname(os.path.abspath(__file__))
		return os.path.abspath(os.path.join(scriptpath, "../data/" + TEMPLATE_FOLDER_NAME))


	def inputFilePath(self):
		"""Returns path to the project's input file `<targetDirPath>/<modelName>.input`."""
		return os.path.join(self.targetDirPath, self.modelName + ".input")


	def generate(self):

		""" Main FMU generation function, creates a new FMU project. Requires member variables to be set correctly.

		Functionality: first a template folder structure is copied to the target location. Then,
		placeholders in the original files are substituted and the generated files
		(modelDescription.xml, <modelName>_generated.h/.cpp) are written.

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

		templateDirPath = self.templateDirPath()
		self.printMsg("Template location  : {}".format(templateDirPath))

		# user may have specified "FMI_template" as model name
		# (which would be weird and break the code, hence a warning)
		if self.modelName == TEMPLATE_FOLDER_NAME:
			self.printMsg("WARNING: model name is same as template folder name. This may not work!")

		self.printMsg("Copying template directory to target directory (and renaming files)")
		self.copyTemplateDirectory(templateDirPath)

		self.printMsg("Adjusting template files (replacing model name)")
		self.substitutePlaceholders()

		self.printMsg("Generating unique value references")
		self.assignValueReferences()

		self.printMsg("Generating modelDescription.xml and {}{}.h/.cpp".format(self.modelName, GENERATED_FILE_SUFFIX))
		self.writeGeneratedFiles(templateDirPath)

		# store input data into <targetDirPath>/<modelName>.input so that it can be read again by wizard to
		# populate input data
		self.writeInputData(self.inputFilePath())

		if self.autobuild:
			self.printMsg("Test-building FMU")
			self.testBuildFMU()

		# *** Done with FMU generation ***


	def update(self, projectDir):
		"""Updates an existing FMU project in directory `projectDir`. Requires modelName and variables to be set
		(e.g. via readInputData()).

		Only generated files are overwritten: `data/modelDescription.xml`, `src/<modelName>_generated.h/.cpp` and
		the project's `<modelName>.input` file. Previous versions of these files are copied to
		`<projectDir>/.backup/<timestamp>/` first. User code files are never touched.

		Projects created with the old template (no `<modelName>_generated.h`) are detected and only the
		generated files are written; the user must migrate the code manually (instructions are printed).
		"""

		if self.modelName == "":
			raise RuntimeError("Missing model name")

		self.targetDirPath = os.path.abspath(projectDir)
		self.printMsg("Project directory  : {}".format(self.targetDirPath))
		if not os.path.isdir(self.targetDirPath):
			raise RuntimeError("Project directory '{}' does not exist.".format(self.targetDirPath))

		userCppFile = os.path.join(self.targetDirPath, "src", self.modelName + ".cpp")
		if not os.path.isfile(userCppFile):
			raise RuntimeError("Missing source file '{}'. Is the model name correct?".format(userCppFile))

		generatedHeader = os.path.join(self.targetDirPath, "src", self.modelName + GENERATED_FILE_SUFFIX + ".h")
		# legacy project: created with FMICodeGenerator <= 1.3 (no generated header, value reference defines in user code)
		with open(userCppFile, 'r', encoding='utf-8') as fobj:
			legacyProject = not os.path.isfile(generatedHeader) or "#define FMI_" in fobj.read()
		if legacyProject:
			self.printMsg("WARNING: Project was created with an older version of FMICodeGenerator (variable defines in "
						  "src/{}.cpp, or no file '{}').".format(self.modelName, os.path.basename(generatedHeader)))

		templateDirPath = self.templateDirPath()
		self.printMsg("Template location  : {}".format(templateDirPath))

		# backup files that will be overwritten
		filesToOverwrite = [
			os.path.join("data", "modelDescription.xml"),
			os.path.join("src", self.modelName + GENERATED_FILE_SUFFIX + ".h"),
			os.path.join("src", self.modelName + GENERATED_FILE_SUFFIX + ".cpp"),
			self.modelName + ".input"
		]
		self.backupFiles(filesToOverwrite)

		self.printMsg("Generating unique value references")
		self.assignValueReferences()

		self.printMsg("Generating modelDescription.xml and {}{}.h/.cpp".format(self.modelName, GENERATED_FILE_SUFFIX))
		self.writeGeneratedFiles(templateDirPath)

		self.writeInputData(self.inputFilePath())

		# check whether user code still contains definitions that are now provided by the generated code
		# (projects created with older versions of FMICodeGenerator)
		conflicts = self.findGeneratedDefinitionsInUserCode(userCppFile)
		if legacyProject or conflicts:
			self.printMigrationInstructions(legacyProject, conflicts)
			self.printMsg("Test-build skipped, the project will not build correctly until it has been migrated.")
			return

		if self.autobuild:
			self.printMsg("Test-building FMU")
			self.testBuildFMU()


	def findGeneratedDefinitionsInUserCode(self, userCppFile):
		"""Returns a list of definitions in the user's .cpp file that are provided by the generated code
		(these lead to duplicate symbol errors and must be removed from the user code)."""
		try:
			with open(userCppFile, 'r', encoding='utf-8') as fobj:
				code = fobj.read()
		except Exception as e:
			raise RuntimeError("Error reading file '{}': {}".format(userCppFile, e))
		candidates = [
			"InstanceData::GUID",
			"InstanceData::create()",
			"{}::computeFMUStateSize()".format(self.modelName),
			"{}::serializeFMUstate(".format(self.modelName),
			"{}::deserializeFMUstate(".format(self.modelName)
		]
		return [c.rstrip('(') for c in candidates if c in code]


	def printMigrationInstructions(self, legacyProject, conflicts):
		"""Prints instructions for manually migrating user code created with older generator versions."""
		m = self.modelName
		gen = m + GENERATED_FILE_SUFFIX
		self.printMsg("")
		self.printMsg("*** Manual migration of your code is required ***")
		self.printMsg("Your source files src/{0}.cpp/.h were not modified. To use the generated files:".format(m))
		step = 1
		if legacyProject:
			self.printMsg("  {}. In src/{}.cpp remove the '#define FMI_...' block.".format(step, m)); step += 1
			self.printMsg("  {}. Move the start value initialization from the constructor into a call to "
						  "'initFMIVariables();'.".format(step)); step += 1
		if conflicts:
			self.printMsg("  {}. In src/{}.cpp remove these definitions, they are now generated in src/{}.cpp:".format(step, m, gen))
			step += 1
			for c in conflicts:
				self.printMsg("       {}".format(c))
			self.printMsg("     Also remove the SERIALIZE/DESERIALIZE macros and the function template deserializeMap(), if present.")
			self.printMsg("  {}. Move your own serialization code (the former 'TODO' sections) into these new member functions "
						  "of src/{}.cpp:".format(step, m)); step += 1
			self.printMsg("       size_t {}::userStateSize() const;".format(m))
			self.printMsg("       void {}::serializeUserState(char * & dataPtr) const;".format(m))
			self.printMsg("       bool {}::deserializeUserState(const char * & dataPtr);".format(m))
		if legacyProject:
			self.printMsg("  {}. In src/{}.h add '#include \"{}.h\"'.".format(step, m, gen)); step += 1
		self.printMsg("  {}. Make sure that src/{}.h declares these member functions:".format(step, m)); step += 1
		for decl in ["void initFMIVariables();",
					 "void readFMIVariables(FMIVariables & v) const;",
					 "void writeFMIVariables(const FMIVariables & v);",
					 "size_t userStateSize() const;",
					 "void serializeUserState(char * & dataPtr) const;",
					 "bool deserializeUserState(const char * & dataPtr);",
					 "virtual void computeFMUStateSize();",
					 "virtual void serializeFMUstate(void * FMUstate);",
					 "virtual bool deserializeFMUstate(void * FMUstate);"]:
			self.printMsg("       " + decl)
		if legacyProject:
			self.printMsg("  {}. Add src/{}.cpp to CMakeLists.txt and {}.pro.".format(step, gen, m)); step += 1
			self.printMsg("  {}. Optionally use readFMIVariables()/writeFMIVariables() in updateIfModified() and "
						  "integrateTo().".format(step)); step += 1
		self.printMsg("See data/FMI_template/src/FMI_template.cpp/.h of FMICodeGenerator for a reference.")


	def backupFiles(self, relPaths):
		"""Copies existing files (paths relative to self.targetDirPath) into
		`<targetDirPath>/.backup/<timestamp>/`, keeping the relative paths."""

		timeStamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
		backupDir = os.path.join(self.targetDirPath, BACKUP_DIR_NAME, timeStamp)
		backedUp = False
		for relPath in relPaths:
			src = os.path.join(self.targetDirPath, relPath)
			if not os.path.isfile(src):
				continue
			dst = os.path.join(backupDir, relPath)
			try:
				os.makedirs(os.path.dirname(dst), exist_ok=True)
				shutil.copy2(src, dst)
				backedUp = True
			except Exception as e:
				raise RuntimeError("Cannot create backup of file '{}': {}".format(src, e))
		if backedUp:
			self.printMsg("Backup of previous files in '{}'".format(backupDir))


	def assignValueReferences(self):
		"""Assigns unique value references to all variables with valueRef == -1 (auto-numbering, starting with 1).

		Already assigned value references are kept, so that value references remain stable across project updates.
		"""
		# first create a set of all predefined valueReferences
		valueRefs = set()
		for var in self.variables:
			if var.valueRef != -1:
				if var.valueRef in valueRefs:
					raise RuntimeError("Duplicate value reference {} (variable '{}').".format(var.valueRef, var.name))
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


	def copyTemplateDirectory(self, templatePath):
		"""Copies the template folder to the new location. Replaces the old name of directories, files
		and script in the files with the newly user defined name (i.e.modelName).

		Path to target directory is stored in self.targetDirPath.
		If target directory exists already and self.overwrite is True, it is moved to trash first,
		otherwise an exception is raised.

		Const-function, does not modify the state of the object.

		Arguments:

		templatePath -- The absolute path to the template directory.

		Example::

		   self.copyTemplateDirectory("../data/FMI_template")
		   # will rename "FMI_template" to "testFMU" after copying
		"""

		# check if target directory exists already
		if os.path.exists(self.targetDirPath):
			if not self.overwrite:
				raise RuntimeError("Target directory '{}' exists already. Use update to modify an existing FMU project."
								   .format(self.targetDirPath))
			try:
				# Move folder to thrash
				send2trash(self.targetDirPath)
			except Exception as e:
				raise RuntimeError("Cannot move existing target directory to trash: {}".format(e))

		try:
			# if parent directory does not yet exist, create it
			parentDir = os.path.dirname(self.targetDirPath)
			if not os.path.exists(parentDir):
				os.makedirs(parentDir)
			# Copy source folder to a new location(i.e. self.targetDirPath)
			shutil.copytree(templatePath, self.targetDirPath)
			# Set modified time of newly created folder
			os.utime(self.targetDirPath, None)
		except Exception as e:
			raise RuntimeError("Cannot copy template directory to target directory: {}".format(e))

		try:
			# rename files that must be named according as the modelName
			os.rename(os.path.join(self.targetDirPath, TEMPLATE_FOLDER_NAME + ".pro"),
					  os.path.join(self.targetDirPath, self.modelName + ".pro"))
			for fname in [".cpp", ".h", GENERATED_FILE_SUFFIX + ".cpp", GENERATED_FILE_SUFFIX + ".h"]:
				os.rename(os.path.join(self.targetDirPath, "src", TEMPLATE_FOLDER_NAME + fname),
						  os.path.join(self.targetDirPath, "src", self.modelName + fname))
		except Exception as e:
			raise RuntimeError("Cannot rename template files: {}".format(e))


	def substitutePlaceholders(self):
		"""Processes all files in the newly copied project directory and replaces the template name with
		the model name. The generated files are written afterwards by writeGeneratedFiles().
		"""

		# loop to walk through the new folder
		for root, dirs, files in os.walk(self.targetDirPath):
			# process all files
			for f in files:

				# compose full file path
				src = os.path.join(root, f)

				try:
					# read file into memory, variable 'data'
					with open(src, 'r', encoding='utf-8') as fobj:
						data = fobj.read()
				except Exception as e:
					self.printMsg(str(e))
					raise RuntimeError("Error reading file: {}".format(src))

				# generic data adjustment
				newData = data.replace(TEMPLATE_FOLDER_NAME, self.modelName)
				if newData == data:
					continue

				try:
					with open(src, 'w', encoding="utf-8") as fobj:
						fobj.write(newData)
				except Exception as e:
					self.printMsg("Error writing file: {}".format(str(e)))
					raise RuntimeError("Error writing file: {}".format(src))


	def writeGeneratedFiles(self, templatePath):
		"""Generates the files owned by the generator from their template counterparts and writes them into
		the project directory (overwriting existing files):

		- data/modelDescription.xml
		- src/<modelName>_generated.h
		- src/<modelName>_generated.cpp

		All files share a newly generated GUID.
		"""

		# Generate globally unique identifier
		guid = uuid.uuid4()

		# Generate time stamp (ISO 8601, UTC)
		localTime = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

		# annotate variables with C++ specific properties
		self.prepareCppVariables()

		def readTemplate(relPath):
			path = os.path.join(templatePath, relPath)
			try:
				with open(path, 'r', encoding='utf-8') as fobj:
					return fobj.read().replace(TEMPLATE_FOLDER_NAME, self.modelName)
			except Exception as e:
				raise RuntimeError("Error reading template file '{}': {}".format(path, e))

		def writeTarget(relPath, data):
			path = os.path.join(self.targetDirPath, relPath)
			try:
				os.makedirs(os.path.dirname(path), exist_ok=True)
				with open(path, 'w', encoding='utf-8') as fobj:
					fobj.write(data)
			except Exception as e:
				raise RuntimeError("Error writing file '{}': {}".format(path, e))

		mdPath = os.path.join("data", "modelDescription.xml")
		writeTarget(mdPath, self.adjustModelDescription(readTemplate(mdPath), localTime, guid))

		hPath = os.path.join("src", TEMPLATE_FOLDER_NAME + GENERATED_FILE_SUFFIX + ".h")
		writeTarget(hPath.replace(TEMPLATE_FOLDER_NAME, self.modelName),
					self.generateVariablesHeader(readTemplate(hPath)))

		cppPath = os.path.join("src", TEMPLATE_FOLDER_NAME + GENERATED_FILE_SUFFIX + ".cpp")
		writeTarget(cppPath.replace(TEMPLATE_FOLDER_NAME, self.modelName),
					self.generateVariablesSource(readTemplate(cppPath), guid))


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
		data = data.replace("$$version$$","1.3.0")
		data = data.replace("$$author$$","not specified")
		data = data.replace("$$copyright$$","not specified")
		data = data.replace("$$license$$","not specified")


		# generate scalar variable section

		VARIABLE_TEMPLATE = """
		<!-- Index of variable = "$$index$$" -->
		<ScalarVariable
			name="$$name$$"$$desc$$
			valueReference="$$valueRef$$"
			variability="$$variability$$"
			causality="$$causality$$"
			initial="$$initial$$">
			<$$typeID$$$$start$$$$unit$$/>
		</ScalarVariable>
		"""

		MODEL_STRUCTURE_OUTPUTS_TEMPLATE = """<Outputs>
			<!-- dependencies must be defined for all output quantities. 'dependencyKind' is only needed
				when some dependencies are constant factors or parameters.
			-->
$$outputUnknowns$$
		</Outputs>"""

		MODEL_STRUCTURE_OUTPUTS_UNKNOWN_TEMPLATE = """			<Unknown index="$$index$$" dependencies="$$dependlist$$"/>"""

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

			if len(var.description) != 0:
				varDefBlock = varDefBlock.replace("$$desc$$", '\n            description="{}"'.format(var.description))
			else:
				varDefBlock = varDefBlock.replace("$$desc$$","")

			# generate value if auto-numbered
			assert(var.valueRef != -1)
			varDefBlock = varDefBlock.replace("$$valueRef$$",str(var.valueRef))

			if var.causality == "input":
				dependList = dependList + " " + str(idx)

			varDefBlock = varDefBlock.replace("$$variability$$",var.variability)
			varDefBlock = varDefBlock.replace("$$causality$$",var.causality)
			varDefBlock = varDefBlock.replace("$$initial$$",var.initial)

			varDefBlock = varDefBlock.replace("$$typeID$$",var.typeID)

			if var.typeID == 'Real' and len(var.unit) > 0:
				varDefBlock = varDefBlock.replace("$$unit$$",' unit="{}"'.format(var.unit))
			else:
				varDefBlock = varDefBlock.replace("$$unit$$","")

			if var.initial=="calculated":
				varDefBlock = varDefBlock.replace("$$start$$","")
			else:
				varDefBlock = varDefBlock.replace("$$start$$",' start="{}"'.format(var.startValue))

			scalarVariableDefs = scalarVariableDefs + "\n" + varDefBlock

		data = data.replace("$$scalarVariables$$",scalarVariableDefs)

		dependList = dependList.strip()

		# output dependency block
		# we first generate the individual '<Unknown index=....' lines, and insert these later in
		# the model structure template
		modelStructureDefs = ""
		modelOutputUnknowns = ""
		for var in self.variables:
			if var.causality == "output":
				dependsDef = MODEL_STRUCTURE_OUTPUTS_UNKNOWN_TEMPLATE
				dependsDef = dependsDef.replace("$$index$$",str(var.idx))
				dependsDef = dependsDef.replace("$$dependlist$$", dependList)
				modelOutputUnknowns = modelOutputUnknowns + "\n" + dependsDef
		# modelOutputUnkowns may be empty, if we do not have any outputs. In this case,
		# we replace the placeholder with an empty string. Otherwise we populate it first.
		if len(modelOutputUnknowns) != 0:
			modelStructureDefs = MODEL_STRUCTURE_OUTPUTS_TEMPLATE.replace("$$outputUnknowns$$", modelOutputUnknowns)
		data = data.replace("$$outputDependencies$$", modelStructureDefs)

		return data


	def prepareCppVariables(self):
		"""Annotates all variables with C++ specific properties used by the source code generators:

		- varDefine   -- name of the value reference define, e.g. FMI_INPUT_T (empty if not used in C++ code)
		- cppType     -- C++ type of the member in struct FMIVariables
		- cppMap      -- name of the InstanceData map holding the variable's value
		- writable    -- True, if writeFMIVariables() stores the variable's value back into the FMU
		"""
		DEFINE_PREFIXES = {
			"input" : "FMI_INPUT",
			"output" : "FMI_OUTPUT",
			"parameter" : "FMI_PARA",
			"calculatedParameter" : "FMI_PARA",
			"local" : "FMI_LOCAL"
		}
		TYPES = {
			# typeID : (map name, C++ type)
			"Real" : ("m_realVar", "double"),
			"Boolean" : ("m_boolVar", "bool"),
			"Integer" : ("m_integerVar", "int"),
			"String" : ("m_stringVar", "std::string")
		}
		for var in self.variables:
			if var.typeID not in TYPES:
				raise RuntimeError("Unsupported type '{}' of variable '{}'.".format(var.typeID, var.name))
			var.cppMap, var.cppType = TYPES[var.typeID]
			if var.causality in DEFINE_PREFIXES:
				var.varDefine = "{}_{}".format(DEFINE_PREFIXES[var.causality], var.name)
			else:
				var.varDefine = "" # variable will not be used in cpp code
			var.writable = var.causality in ["output", "calculatedParameter", "local"]


	def generateVariablesHeader(self, data):
		"""Adjusts content of the `<modelName>_generated.h` template.
		Replaces the following placeholders:

		- $$defines$$ - defines with value references for each published variable
		- $$structMembers$$ - members of struct FMIVariables

		Requires prepareCppVariables() to be called before.
		"""
		defines = []
		members = []
		for var in self.variables:
			if not var.varDefine:
				continue
			defines.append("#define {} {}".format(var.varDefine, var.valueRef))
			comment = var.causality
			if var.typeID == "Real" and var.unit:
				comment += ", unit: " + var.unit
			if var.description:
				comment += ", " + var.description
			members.append("\t{} {}; // {}".format(var.cppType, var.name, comment))
		data = data.replace("$$defines$$", "\n".join(defines))
		data = data.replace("$$structMembers$$", "\n".join(members))
		return data


	def generateVariablesSource(self, data, guid):
		"""Adjusts content of the `<modelName>_generated.cpp` template.
		Replaces the following placeholders:

		- $$GUID$$ - globally unique identifier (must match the GUID in modelDescription.xml)
		- $$initialization$$ - start values for all variables
		- $$readVars$$ - copies values of all variables into struct FMIVariables
		- $$writeVars$$ - stores outputs, calculated parameters and local variables from struct FMIVariables

		Requires prepareCppVariables() to be called before.
		"""

		data = data.replace("$$GUID$$", str(guid))

		def cppStringLiteral(s):
			return '"' + s.replace('\\', '\\\\').replace('"', '\\"') + '"'

		initLines = []
		readLines = []
		writeLines = []
		for var in self.variables:
			if not var.varDefine:
				continue
			mapAccess = "{}[{}]".format(var.cppMap, var.varDefine)
			# initialization with start value
			if var.typeID == "String":
				startValue = cppStringLiteral(var.startValue)
			else:
				# we expect start value to be a valid number/boolean literal, otherwise we default to 0
				startValue = var.startValue.strip()
				if len(startValue) == 0:
					startValue = "0"
				if var.typeID == "Boolean":
					startValue = "1" if startValue.lower() in ["true", "1"] else "0"
			initLines.append("\t{} = {};".format(mapAccess, startValue))

			# read access
			if var.typeID == "Boolean":
				readLines.append("\tv.{} = ({}.at({}) != 0);".format(var.name, var.cppMap, var.varDefine))
			else:
				readLines.append("\tv.{} = {}.at({});".format(var.name, var.cppMap, var.varDefine))

			# write access
			if var.writable:
				if var.typeID == "Boolean":
					writeLines.append("\t{} = v.{} ? 1 : 0;".format(mapAccess, var.name))
				else:
					writeLines.append("\t{} = v.{};".format(mapAccess, var.name))

		# avoid unused parameter warnings if there is nothing to read or write
		if not readLines:
			readLines.append("\t(void)v;")
		if not writeLines:
			writeLines.append("\t(void)v;")

		data = data.replace("$$initialization$$", "\n".join(initLines))
		data = data.replace("$$readVars$$", "\n".join(readLines))
		data = data.replace("$$writeVars$$", "\n".join(writeLines))
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
				result = subprocess.run(["build_VC_x64.bat"], shell=True, creationflags=subprocess.CREATE_NEW_CONSOLE,
										cwd=buildDir, capture_output=True, text=True)

				# if return code is different from 0, print the error message
				if result.returncode != 0:
					self.printMsg(result.stdout + "\n" + result.stderr)
					raise RuntimeError("Error during compilation of FMU.")

				self.printMsg("Compiled FMU successfully")

				# call batch file to deploy the FMI library
				result = subprocess.run(["deploy.bat"], shell=True, creationflags=subprocess.CREATE_NEW_CONSOLE,
										cwd=buildDir, capture_output=True, text=True)

				if result.returncode != 0:
					self.printMsg(result.stdout + "\n" + result.stderr)
					raise RuntimeError("Error during compilation of FMU")

				self.printMsg("Successfully created {}".format(self.modelName + ".fmu"))

			else:
				# shell file execution for Mac & Linux
				result = subprocess.run(["bash", "./build.sh"], cwd=buildDir, capture_output=True, text=True)

				if result.returncode != 0:
					self.printMsg(result.stderr)
					raise RuntimeError("Error during compilation of FMU")

				self.printMsg("Compiled FMU successfully")

				# Deployment

				# shell file execution for Mac & Linux
				deploy = subprocess.run(["bash", "./deploy.sh"], cwd=buildDir, capture_output=True, text=True)

				if deploy.returncode != 0:
					self.printMsg(deploy.stderr)
					raise RuntimeError("Error during assembly of FMU")

				self.printMsg("Successfully created {}".format(self.modelName + ".fmu"))

		except Exception as e:
			self.printMsg(str(e))
			self.printMsg("Error building FMU.")
			raise



	def writeInputData(self, targetFile):
		"""Writes all input data to FMIGenerator to file so it can be read later by the FMIGeneratorWizard to
		populate the dialog again (and to update the project later)."""

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

		with open(targetFile, 'w', encoding='utf-8') as outfile:
			json.dump(data, outfile, indent=4)


	def readInputData(self, targetFile):
		with open(targetFile, 'r', encoding='utf-8') as f:
			data = json.load(f)
			if 'modelName' in data:
				self.modelName = data['modelName']
			self.description = data['description']
			self.variables = []
			for a in data['variables']:
				v = varDefFromJson(a)
				self.variables.append(v)
