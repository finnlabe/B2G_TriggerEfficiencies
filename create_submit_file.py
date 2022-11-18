import argparse
import os

# the same inputs that will be passed on to the runTriggerEfficiencies script, only that --input is a folder directory!

parser = argparse.ArgumentParser()

parser.add_argument('-i', '--inputFolder', required=True)
parser.add_argument('-e', '--era', required=True)
parser.add_argument('-o', '--output', required=True)

parser.add_argument('--doJECs', action='store_true')
parser.add_argument('--useGoldenJSON', action='store_true')

parser.add_argument('--storeVariables', action='store_true')

args = parser.parse_args()

# build the text file

with open(args.output, "w") as outfile:

    outfile.write( 'executable = condor.sh' + '\n' )
    outfile.write( 'arguments = filelist_$(Process).txt refTriggers.txt testTriggers.txt ' + args.era + ' $(Process) ' )

    additional_options = ""
    if(args.doJECs): additional_options += " --doJECs"
    if(args.useGoldenJSON): additional_options += " --useGoldenJSON"
    if(args.storeVariables): additional_options += " --storeVariables"
    if(additional_options == ""): additional_options = "none"

    outfile.write( additional_options + ' \n' )

    outfile.write( 'output = log/B2G_' + args.era + '_triggereff.$(Process).out' + '\n' )
    outfile.write( 'error = log/B2G_' + args.era + '_triggereff.$(Process).out' + '\n' )
    outfile.write( 'log = log/B2G_' + args.era + '_triggereff.log' + '\n' )
    outfile.write( '+JobFlavour = "espresso"' + '\n' )
    outfile.write( 'use_x509userproxy = true' + '\n' )
    outfile.write( 'x509userproxy = ' + os.path.expanduser('~') + '/x509up_u103872' + '\n' )
    outfile.write( 'transfer_input_files = runTriggerEfficiencies.py, helpers.py, core.py, data, ' + args.inputFolder + '/file_lists/filelist_$(Process).txt, ' + args.inputFolder + '/refTriggers.txt, ' + args.inputFolder + '/testTriggers.txt' + '\n' )
    outfile.write( 'transfer_output_files = output_' + args.era + '_$(Process).root' + '\n' )
    outfile.write( 'should_transfer_files = YES' + '\n' )
    outfile.write( 'when_to_transfer_output = ON_EXIT' + '\n' )
    _, _, files = next(os.walk( args.inputFolder + '/file_lists/' ))
    outfile.write( 'queue ' + str( len(files) ) + '\n' )