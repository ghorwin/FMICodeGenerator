#!/usr/bin/python

import argparse
from FMIGenerator import FMIGenerator

# commandline argument parser
parser = argparse.ArgumentParser()
parser.add_argument("modelName", type=str, help="ID Name of FMU, will be used for directory names, generated FMU name and model name.")
parser.add_argument("--description", type=str, help="Description of FMU")
args = parser.parse_args()

# create storage class instance
fmiGenerator = FMIGenerator()

# store command line arguments
fmiGenerator.modelName = args.modelName
if args.description!=None:
	fmiGenerator.description = args.description

# call function of generator to create model
fmiGenerator.generate()






