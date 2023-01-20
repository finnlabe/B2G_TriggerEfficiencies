import coffea
import awkward as ak
import numpy as np
from coffea.nanoevents import NanoEventsFactory, NanoAODSchema
from coffea.lumi_tools import LumiMask
from coffea.lookup_tools import extractor
from coffea.jetmet_tools import JECStack, CorrectedJetsFactory
import os
import sys

from helpers import *

# main function running on a single input file
def run_one_file(inputfile, refTriggers, testTriggers, goldenJSON=None, JECcorrectionpath=None):

    #########################
    ####  Event reading  ####
    #########################

    # as xrootd connections are often rather unstable, there are several different tricks here to try and address that
    try:
        # first, lets try to stream the file
        events = NanoEventsFactory.from_root(
            inputfile.replace("xrootd-cms.infn.it", "cmsxrootd.fnal.gov"),
            schemaclass=NanoAODSchema,
        ).events()
    except OSError as error:
        # if streaming is not working, try copying over the entire file
        print(error)
        print("Trying with local copy")
        os.system('xrdcp "'+inputfile.replace("xrootd-cms.infn.it", "cmsxrootd.fnal.gov")+'" input.root')
        try:
            events = NanoEventsFactory.from_root(
                "input.root",
                schemaclass=NanoAODSchema,
            ).events()
        except OSError as error:
            # if that is also not working, just ignore the file
            print(error)
            os.system("rm input.root")
            return False, False, False, False
        os.system("rm input.root")


    #######################
    ####  golden JSON  ####
    #######################
    
    if goldenJSON:
        lumiMask = LumiMask(goldenJSON)
        applied_lumiMask = lumiMask(events.run, events.luminosityBlock)

        events = events[applied_lumiMask]
    
    ################
    ####  JECs  ####
    ################
    
    if JECcorrectionpath:
        print("Doing JECs...")

        # getting list of corrections from appropriate folder
        corrections_list = make_corrections_list(JECcorrectionpath)

        # TODO maybe put a cross-check in here that compares runs

        # extract corrections
        ext = extractor()
        ext.add_weight_sets(corrections_list)
        ext.finalize()

        # create corrected jet factory
        jec_stack = JECStack(ext.make_evaluator())
        jet_factory  = CorrectedJetsFactory(get_jec_name_map(), jec_stack)
        events_cache = events.caches[0]

        # rho is stored differently for run 2 and run 3
        if ("22" in JECcorrectionpath): rhos = events.Rho.fixedGridRhoFastjetAll
        elif ("18" in JECcorrectionpath): rhos = events.fixedGridRhoFastjetAll

        # get corrected jets
        corrected_FatJets = jet_factory.build(add_jec_variables(events.FatJet,
                                                                rhos,
                                                                True),
                                              events_cache)

        # overwrite previous jet collection with corrected ones
        events.FatJet = corrected_FatJets


    #########################
    ####  Ref. triggers  ####
    #########################

    cleanedRefTriggers = []
    for trigger in refTriggers:
        if trigger in events.HLT.fields: cleanedRefTriggers.append(trigger)
        else: print("Not using " + trigger + " as its not available in the sample")
    if (len(cleanedRefTriggers) == 0):
        return False, False, False, False
    
    # getting the trigger masks and taking OR
    ref_masks = np.asarray( [events.HLT[trigger].to_numpy() for trigger in cleanedRefTriggers] )
    ref_mask = np.any(ref_masks, axis=0)
    
    # applying ref trigger mask
    events = events[ref_mask]

    ###############################
    ####  Collection cleaning  ####
    ###############################

    # jet ID selection
    FatJet_mask = events.FatJet.isTightLeptonVeto
    selected_FatJets = events.FatJet[ FatJet_mask ]
    events.FatJet = selected_FatJets

    
    #####################
    ####  Selection  ####
    #####################
    
    # calculate some variables for cuts
    leading_AK8_pt = ak.pad_none( events.FatJet.pt, 1, axis=1)[:,0]
    leading_AK8_eta = ak.pad_none( events.FatJet.eta, 1, axis=1)[:,0]
    
    # leading jet is required to have > 200 GeV and abs(eta) < 2.4
    jet_cut_pt_mask = ( ak.fill_none(leading_AK8_pt, -1) > 200 ).to_numpy()
    jet_cut_eta_mask = ( abs( ak.fill_none(leading_AK8_eta, 99999) ) < 2.4 ).to_numpy()

    # we need muon variables to ensure a muon cut > 30 GeV
    leading_mu_pt = ak.pad_none( events.Muon.pt, 1, axis=1)[:,0]
    muon_cut_pt_mask = ( ak.fill_none(leading_mu_pt, -1) > 30 ).to_numpy()
    
    # combining all cut masks
    selection_mask = np.logical_and.reduce((jet_cut_pt_mask, jet_cut_eta_mask, muon_cut_pt_mask))
    
    # applying the selection
    events = events[selection_mask]
    
    #########################
    ####  Test triggers  ####
    #########################

    cleanedTestTriggers = []
    for trigger in testTriggers:
        if trigger in events.HLT.fields: cleanedTestTriggers.append(trigger)
        else: print("Not using " + trigger + " as its not available in the sample")
    if (len(cleanedTestTriggers) == 0): raise Exception("No valid ref triggers found!")
    
    trigger_masks_bits = [ events.HLT[trigger].to_numpy() for trigger in cleanedTestTriggers ]
    trigger_masks = dict( zip(testTriggers, trigger_masks_bits) )
    
    
    ################################
    ####  Variable calculation  ####
    ################################
    
    # get pt, eta and mSD of the leading jet
    leading_AK8_pt = ak.pad_none( events.FatJet.pt, 1, axis=1)[:,0]
    leading_AK8_eta = ak.pad_none( events.FatJet.eta, 1, axis=1)[:,0]
    leading_AK8_mSD = ak.pad_none( events.FatJet.msoftdrop, 1, axis=1)[:,0]
    
    # AK8 jet HT
    AK8_HT = ak.sum( events.FatJet.pt, axis=1)

    # pile up
    nPV = events.PV.npvs
    
    
    #####################
    ####  Returning  ####
    #####################
    
    names = ["leading AK8 pt", "leading AK8 eta", "leading AK8 mSD", "AK8 HT", "nPV"]
    
    binning = [
        [edge for edge in np.arange(0, 700, 25)] + [edge for edge in np.arange(700, 1000, 100)] + [edge for edge in np.arange(1000, 1750, 250)],
        [edge for edge in np.arange(-4, 4, 0.25)],
        [edge for edge in np.arange(0, 600, 25)],
        [edge for edge in np.arange(0, 3000, 100)],
        [edge for edge in np.arange(0, 40, 10)] + [edge for edge in np.arange(40, 75, 5)] + [100],
    ]

    values = [leading_AK8_pt, leading_AK8_eta, leading_AK8_mSD, AK8_HT, nPV]

    # we'll just output data so histogramming and efficiency calculation can be made offline
    return names, binning, values, trigger_masks
    
# running on multiple input files and combining the output
def run_multiple_files(inputfiles, refTriggers, testTriggers, goldenJSON=None, JECcorrectionpath=None):
    
    all_values = []
    all_masks = []
    
    # main loop over all input files of this job
    for inputfile in inputfiles:
        
        print("Starting to process " + inputfile + ".")
        
        # getting the results of one job
        names, binnings, values, masks = run_one_file(inputfile,
                                     refTriggers,
                                     testTriggers,
                                     goldenJSON,
                                     JECcorrectionpath)
              
        if names: # in case individual file failed, skip
            all_values.append(values)
            all_masks.append(masks)        
            safety_names = names # in case the last is broken, we want to use the one before that
            safety_binnings = binnings

    if(len(all_values) == 0): raise Exception("No file in this job yielded any results")

    # fix issue if last return was "false", but others were fine
    if not names:
        names = safety_names
        binnings = safety_binnings

    print("Done processing all files. Combining outputs.")
        
    # now, lets concatenate all returns together
    # I am sure there is a nicer way for this, might revisit in the future
    final_values = []
    for i in range(len(names)):
        
        temp_values = []
        for file_values in all_values:
            temp_values.append( file_values[i] )
            
        total_temp_values = ak.concatenate(temp_values, axis=0)
        final_values.append(total_temp_values)
        
    # similar thing for trigger masks
    final_masks = {}
    for trigger in testTriggers:
        
        temp_masks = []
        for file_masks in all_masks:
            temp_masks.append( file_masks[trigger] )
            
        total_temp_values = ak.concatenate(temp_masks, axis=0)
        final_masks[trigger] = total_temp_values
                
    return names, binnings, final_values, final_masks
