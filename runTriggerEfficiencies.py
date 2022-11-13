import coffea
import awkward as ak
import numpy as np
from coffea.nanoevents import NanoEventsFactory, NanoAODSchema
from coffea.lumi_tools import LumiMask
from coffea.lookup_tools import extractor
from coffea.jetmet_tools import JECStack, CorrectedJetsFactory
import os
import sys
import argparse

from helpers import *
from core import *

#     #####################     #
#     ####  MAIN CODE  ####     #
#     #####################     #

# attention, this module does not to proper error handing yet!
# So make sure the inputs are correct or you will get weird behavior.

# we want at least four inputs (plus thisfile name):
# - input files
# - era
# - ref triggers
# - test triggers
# then some optional ones follow
# - useJECs
# - use

parser = argparse.ArgumentParser()

parser.add_argument('-i', '--input', required=True)
parser.add_argument('-r', '--refTriggers', required=True)
parser.add_argument('-t', '--testTriggers', required=True)
parser.add_argument('-e', '--era', required=True)

parser.add_argument('--doJECs', action='store_true')
parser.add_argument('--useGoldenJSON', action='store_true')

args = parser.parse_args()

# fetch input files
with open(args.input) as file: inputfiles = [line.rstrip() for line in file]
    
# fetch triggers
with open(args.refTriggers) as file: refTriggers = [line.rstrip() for line in file]
with open(args.testTriggers) as file: testTriggers = [line.rstrip() for line in file]

# fetching of correct JEC folder
if args.doJECs:
    JECcorrectionpath = getJECcorrectionpath(args.era)
else:
    JECcorrectionpath = None

# fetching of correct golden JSON file
if args.useGoldenJSON:
    goldenJSON = getGoldenJSON(args.era)
else:
    goldenJSON = None

# run the core part of the core for multiple files
names, values, masks = run_multiple_files(inputfiles,
                       refTriggers,
                       testTriggers,
                       goldenJSON,
                       JECcorrectionpath)

# outputting the results
for name, value in zip(names, values):
    
    with open(name.replace(" ", "__") + '.npy', 'wb') as f:
        np.save(f, np.asarray(value.to_numpy()))
        
for name in masks:
    mask = masks[name]
    
    with open(name + '.npy', 'wb') as f:
        np.save(f, np.asarray(mask.to_numpy()))