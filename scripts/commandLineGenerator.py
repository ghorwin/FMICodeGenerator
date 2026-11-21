#!/usr/bin/env python3

# Main script for generating FMU code. This is the command line version which generates a minimalistic
# barebone of the modelDescription.xml and the implementation files. Currently, command line
# arguments exist only for model name and description (so, no variables in your FMU).
#
# Feel free to copy this file and add code that populates the FMIGenerator.variables array with data before
# calling fmiGenerator.generate()
#
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

import argparse
import sys
from FMIGenerator import *

# commandline argument parser
parser = argparse.ArgumentParser(description="Generates a new FMU project, or updates an existing FMU project.")
parser.add_argument("modelName", type=str, nargs='?',
					help="ID Name of FMU, will be used for directory names, generated FMU name and model name. "
						 "Not needed with --input or --update.")
parser.add_argument("--description", type=str, help="Description of the FMU/model")
parser.add_argument("--target-dir", type=str, default="",
					help="Directory in which the FMU project directory <modelName> is created (default: current directory).")
parser.add_argument("--input", type=str,
					help="Read model name, description and variables from this .input file when creating a new project.")
parser.add_argument("--update", type=str, metavar="PROJECT_DIR",
					help="Update the existing FMU project in PROJECT_DIR using its <modelName>.input file. "
						 "Only generated files are overwritten, user code is kept.")
parser.add_argument("--overwrite", action="store_true",
					help="When creating a new project, move an existing target directory to the trash.")
parser.add_argument("--no-build", action="store_true", help="Skip test-build of the FMU.")
args = parser.parse_args()

# create storage class instance
fmiGenerator = FMIGenerator()
fmiGenerator.autobuild = not args.no_build
fmiGenerator.overwrite = args.overwrite

try:
	if args.update is not None:
		inputFile = findProjectInputFile(args.update)
		if inputFile is None:
			raise RuntimeError("No (unique) .input file found in project directory '{}'.".format(args.update))
		print("Reading project data from '{}'".format(inputFile))
		fmiGenerator.readInputData(inputFile)
		if args.description is not None:
			fmiGenerator.description = args.description
		fmiGenerator.update(args.update)
	else:
		if args.input is not None:
			fmiGenerator.readInputData(args.input)
		if args.modelName is not None:
			fmiGenerator.modelName = args.modelName
		if args.description is not None:
			fmiGenerator.description = args.description
		if not fmiGenerator.description:
			print("WARNING: Model description missing.")
		fmiGenerator.targetDir = args.target_dir

		# setup variables (test code below)
		if False:
			v = VarDef("InputVar1", "continuous", "input", "exact", "Real") # valueRef will be given automatically
			v.startValue = "15"
			fmiGenerator.variables.append(v)

		# call function of generator to create model
		fmiGenerator.generate()
except Exception as e:
	print("ERROR: Error during FMU generation")
	print(e)
	sys.exit(1)
