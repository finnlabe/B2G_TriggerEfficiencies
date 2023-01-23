import argparse
import os

# the same inputs that will be passed on to the runTriggerEfficiencies script, only that --input is a folder directory!

parser = argparse.ArgumentParser()

parser.add_argument('-w', '--workdir', required=True)
parser.add_argument('-e', '--era', required=True)
parser.add_argument('-s', '--submitFile', default="condor.sub")

parser.add_argument('--doJECs', action='store_true')
parser.add_argument('--useGoldenJSON', action='store_true')

parser.add_argument('--storeVariables', action='store_true')

args = parser.parse_args()

# everything should in the end be handled within the workdir
path_workdir = os.path.abspath(args.workdir)
path_home = os.path.abspath(os.getcwd())
print("Creating scripts to run from " + path_workdir)

# build the text file
print("Building the submit file...")

with open(args.submitFile, "w") as outfile:

    outfile.write( 'executable = ' + path_workdir + '/condor.sh' + '\n' )
    outfile.write( 'arguments = $(Process)\n' )
    outfile.write( 'initialdir = ' + path_workdir + '\n' )

    outfile.write( 'output = ' + path_workdir + '/log/joblog_' + args.era + '_triggereff.$(Process).out' + '\n' )
    outfile.write( 'error = ' + path_workdir + '/log/joblog_' + args.era + '_triggereff.$(Process).out' + '\n' )
    outfile.write( 'log = log/totallog_' + args.era + '_triggereff.log' + '\n' )
    outfile.write( '+JobFlavour = "espresso"' + '\n' )
    outfile.write( 'use_x509userproxy = true' + '\n' )
    outfile.write( 'x509userproxy = ' + os.path.expanduser('~') + '/x509up_u103872' + '\n' )
    outfile.write( 'transfer_input_files = ' + path_home + '/runTriggerEfficiencies.py, ' + path_home + '/helpers.py, ' + path_home + '/core.py, ' + path_home + '/data, ' + path_workdir + '/split_file_list/filelist_$(Process).txt, ' + path_workdir + '/refTriggers.txt, ' + path_workdir + '/testTriggers.txt' + '\n' )
    outfile.write( 'transfer_output_files = output_' + args.era + '_$(Process).root' + '\n' )
    outfile.write( 'should_transfer_files = YES' + '\n' )
    outfile.write( 'when_to_transfer_output = ON_EXIT' + '\n' )
    _, _, files = next(os.walk( path_workdir + '/split_file_list/' ))
    outfile.write( 'queue ' + str( len(files) ) + '\n' )

print("Building the shell script that will be executed by condor...")

additional_options = ""
if(args.doJECs): additional_options += " --doJECs"
if(args.useGoldenJSON): additional_options += " --useGoldenJSON"
if(args.storeVariables): additional_options += " --storeVariables"

with open(path_workdir + "/condor.sh", "w") as outfile:
    outfile.write("""#!/bin/bash

# Check input and where we are
export XRD_REQUESTTIMEOUT=1800

# activating the environment
echo "Activating the environment..."
source /cvmfs/sft-nightlies.cern.ch/lcg/views/dev3/latest/x86_64-centos7-gcc11-opt/setup.sh

# we should have all files copied to the work server using the condor submit script
echo "Starting the python script"
python runTriggerEfficiencies.py -i filelist_$1.txt -r refTriggers.txt -t testTriggers.txt -e """ + args.era + " " + additional_options + """

echo "Condor job done, transferring outout..."

# renaming output file according to job ID
mv "output.root" "output_""" + args.era + """_$1.root"

# the transfer back will be done automatically by condor!
""")

# create a directory for the log files

if not os.path.exists(path_workdir + "/log"):

   # Create a new directory because it does not exist
   os.makedirs(path_workdir + "/log")
   print("Created a log directory.")