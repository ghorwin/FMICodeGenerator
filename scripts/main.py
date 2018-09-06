import argparse
from generate import generateFMU

parser = argparse.ArgumentParser()
parser.add_argument("FMUIDName",type=str,help="ID Name of FMU / Model Name")
args = parser.parse_args()

# TODO : get other config options
# - input vars
# - output vars
# - parameters

# call function of generator to create model


generateFMU(args.FMUIDName)

