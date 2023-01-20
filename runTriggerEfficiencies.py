import coffea
import awkward as ak
import numpy as np
import uproot
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

parser.add_argument('--storeVariables', action='store_true')

args = parser.parse_args()

# fetch input files
with open(args.input) as file: inputfiles = [line.rstrip() for line in file]
    
# fetch triggers
with open(args.refTriggers) as file: refTriggers = [line.rstrip() for line in file]
with open(args.testTriggers) as file: testTriggers = [line.rstrip() for line in file]

# fetching of correct JEC folder
if args.doJECs:
    JECcorrectionpath = getJECcorrectionpath(args.era)
    print("Using JECs at " + JECcorrectionpath)
else:
    JECcorrectionpath = None

# fetching of correct golden JSON file
if args.useGoldenJSON:
    goldenJSON = getGoldenJSON(args.era)
    print("Using golden JSON at " + goldenJSON)
else:
    goldenJSON = None

# run the core part of the core for multiple files
names, binnings, values, masks = run_multiple_files(inputfiles,
                                                    refTriggers,
                                                    testTriggers,
                                                    goldenJSON,
                                                    JECcorrectionpath)


# potentially outputting the results
if(args.storeVariables):
    for name, value in zip(names, values):

        with open(name.replace(" ", "__") + '.npy', 'wb') as f:
            np.save(f, np.asarray(value.to_numpy()))

    for name in masks:
        mask = masks[name]

        with open(name + '.npy', 'wb') as f:
            np.save(f, np.asarray(mask.to_numpy()))
            

# creating histograms
# we'll do histograms for two versions: only the cuts applied in the selection above, and an additional m(SD) cut
# we won't create efficiencies here as these need to be created for all jobs combined
# binning areset to some fixed value, defined within the core function
# also, we'll define "pure" histograms, that store only events that a trigger has exclusively triggered when comparing to all others

# create and open root file
with uproot.recreate("output.root") as fout:

    for name, binning, value in zip(names, binnings, values):

        # create histogram and store it to a file
        fout[name.replace(" ", "_") + "__before"] = np.histogram(value.to_numpy(), bins = binning)

        # apply trigger masks and create second histogram
        for trigger in masks:
            fout[name.replace(" ", "_") + "__" + trigger] = np.histogram(value[masks[trigger]].to_numpy(), bins = binning)
    
        # lets also do a "total efficiency" for all considered triggers
        all_masks = []
        for trigger in masks:
            all_masks.append( masks[trigger].to_numpy().reshape(len(masks[trigger]), 1) )
        all_masks_concat = np.concatenate( all_masks, axis=1)
        all_masks_combined = np.any(all_masks_concat, axis=-1)
        fout[name.replace(" ", "_") + "__total"] = np.histogram(value.to_numpy()[all_masks_combined], bins = binning)

        # now lets do the same but as a "pure" efficiency
        for trigger in masks:

            other_masks = []

            for other_trigger in masks:
                if not trigger == other_trigger:
                    other_masks.append( masks[other_trigger].to_numpy().reshape(len(masks[other_trigger]), 1) )

            other_masks_concat = np.concatenate( other_masks, axis=1)
            total_not_others = np.logical_not( np.any(other_masks_concat, axis=-1) )
            total_mask = np.logical_and( masks[trigger], total_not_others  )

            fout[name.replace(" ", "_") + "__" + trigger + "__pure"] = np.histogram(value.to_numpy()[total_mask], bins = binning)

    # now lets do the same for the mSD > 35 situation
    try: 
        mSD_index = names.index("leading AK8 mSD")
        mSD_mask = (values[mSD_index] > 35).to_numpy()
        for name, binning, value in zip(names, binnings, values):

            # create histogram and store it to a file
            fout["mSD35__" + name.replace(" ", "_") + "__before"] = np.histogram(value.to_numpy()[mSD_mask], bins = binning)

            # apply trigger masks and create second histogram
            for trigger in masks:
                # now we need to combine this mask and the trigger mask
                trigger_mask = masks[trigger].to_numpy()
                
                total_mask = np.concatenate((mSD_mask.reshape(mSD_mask.shape[0],1), trigger_mask.reshape(mSD_mask.shape[0],1)), axis=1)
                total_mask = np.all(total_mask, axis=1)

                fout["mSD35__" + name.replace(" ", "_") + "__" + trigger] = np.histogram(value.to_numpy()[total_mask], bins = binning)
    
            # the "all masks combined" from above is still valid here
            # we just need to OR with the mSD35
            all_masks_combined_mSD35 = np.logical_and(all_masks_combined, mSD_mask)
            fout["mSD35__" + name.replace(" ", "_") + "__total"] = np.histogram(value.to_numpy()[all_masks_combined_mSD35], bins = binning)

    except ValueError as error:
        print(error)
        print("Not doing mSD > 35 plots, as no mSD variable found.")
        

