# B2G_TriggerEfficiencies

This repository contains the code to calculate trigger efficiencies that is used by the B2G trigger contacts.
It is using the orthogonal dataset method and mainly targets hadronic triggers, like our jet mass triggers (HLT_AK8PFJet400_MassSD30).

## Installation

The python code used in this framework requires a few packages (and their dependencies), which can be installed using pip or conda.
The needed packages are the following:

- uproot
- coffea
- awkward
- numpy

Additionally, the `xrootd` package is required if files from the GRID are to be used.

(I am currently checking what is available on lxplus, maybe we can use some existing environment -Finn)


## Usage

A single main python file is implemented that executes the desired code: runTriggerEfficiencies.py

This file can be called as `python runTriggerEfficiencies.py`, and requires several arguments afterwards:

- -i or --input: a text file containing a list of input files to run on (one file per line)
- -r or --refTriggers: a text file containing the reference triggers (one trigger per line)
- -t or --testTriggers: a text file containing the triggers to be measured (one trigger per line)
- -e or --era: the data-taking era (a string, for example "22RunD"). Might be auto-detected later

Two additional, optional flags can be set:
- --doJECs: apply jet energy corrections according to the era
- --useGoldenJSON: apply a goldenJSON selection

A complete example command thus could be
`python runTriggerEfficiencies.py -i example/inputfiles.txt -r example/refTriggers.txt -t example/testTriggers.txt -e 22RunD --doJECS --useGoldenJSON`

## Corrections / goldenJSON
Jet energy corrections are applied according to the files in the `data` directory, based on the files obtained from the [JERC group recommendations](https://cms-jerc.web.cern.ch/Recommendations/). In case new ones need to be added, these can be added to the `data/corrections` directory. There, a helper script ([ConvertCorrectionFiles.py](https://github.com/finnlabe/B2G_TriggerEfficiencies/blob/master/data/corrections/ConvertCorrectionFiles.py "ConvertCorrectionFiles.py")) is given to obtain the correct file naming.

The golden JSON selection is made based on the file in `data/goldenJSON`, where new ones can be added.
