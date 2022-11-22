import coffea
import awkward as ak
import numpy as np
from coffea.nanoevents import NanoEventsFactory, NanoAODSchema
from coffea.lumi_tools import LumiMask
from coffea.lookup_tools import extractor
from coffea.jetmet_tools import JECStack, CorrectedJetsFactory
import os
import sys

# some helper functions

def make_corrections_list(directory):
    
    results = []
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".txt") and not file.startswith("._"):
                 if file[:-4].endswith("jec") and "AK8" in file:
                        results.append("* * " + directory + "/" + file)
                      
    return results


def add_jec_variables(jets, event_rho, isData):
    jets["pt_raw"] = (1 - jets.rawFactor)*jets.pt
    jets["mass_raw"] = (1 - jets.rawFactor)*jets.mass
    if not isData:
        jets["pt_gen"] = ak.values_astype(ak.fill_none(jets.matched_gen.pt, 0), np.float32)
    jets["event_rho"] = ak.broadcast_arrays(event_rho, jets.pt)[0]
    return jets

def get_jec_name_map():

    jec_name_map = {
        'JetPt': 'pt',
        'JetMass': 'mass',
        'JetEta': 'eta',
        'JetA': 'area',
        'ptGenJet': 'pt_gen',
        'ptRaw': 'pt_raw',
        'massRaw': 'mass_raw',
        'Rho': 'event_rho',
        'METpt': 'pt',
        'METphi': 'phi',
        'JetPhi': 'phi',
    }
    
    return jec_name_map

def getJECcorrectionpath(era, force = False):
    
    # TODO make these relative
    JECoptions = {
        "22RunC": "data/corrections/22RunC/",
        "22RunD": "data/corrections/22RunD/",
    }
    
    if era in JECoptions:
        return JECoptions[era]
    elif force:
        raise Exception("Era " + era + " not recognized to get JEC")
    else:
        return None
    
def getGoldenJSON(era, force = False):
    
    # at the moment there is just one golden JSON file
    # if at some point this should be split, that can be added here
    if "22" in era:
        return "data/goldenJSON/Cert_Collisions2022_355100_361580_Golden.json"
    elif "18" in era:
        return "data/goldenJSON/Cert_314472-325175_13TeV_Legacy2018_Collisions18_JSON.txt"
    else:
        raise Exception("Era " + era + " not recognized to get golden JSON")

