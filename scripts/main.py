#!/usr/bin/python

import argparse
from generate import generateFMU

parser = argparse.ArgumentParser()
parser.add_argument("ModelName", type=str, help="ID Name of FMU, will be used for directory names, generated FMU name and model name.")
args = parser.parse_args()

# TODO : get other config options
# - input vars
# - output vars
# - parameters

# call function of generator to create model


generateFMU(args.ModelName)

