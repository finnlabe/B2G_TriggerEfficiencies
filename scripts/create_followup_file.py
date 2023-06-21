import argparse
import os
import glob

# the same inputs that will be passed on to the runTriggerEfficiencies script, only that --input is a folder directory!
parser = argparse.ArgumentParser()

parser.add_argument('-w', '--workdir', required=True)
parser.add_argument('-p', '--previousSubmitFile', required=True)
parser.add_argument('-s', '--submitFile', default="condor_followup.sub")

args = parser.parse_args()

# first, lets move through the wordir and delete all empty files that have file size == 0
print("Deleting all empty return files in " + args.workdir + "...")
os.system("find " + args.workdir + " -size 0 -print -delete")

# next, we'll determine which job IDs are still missing
notDone = True
thisID = 0
missingIDs = []
while notDone:
    if os.path.isfile(args.workdir + "/split_file_list/filelist_" + str(thisID) + ".txt"):

        outfiles_for_this_ID = glob.glob(args.workdir + "/output_*_" + str(thisID) + ".root")
        if( len(outfiles_for_this_ID) == 0): missingIDs.append(thisID)

        thisID += 1
    else: notDone = False

if len(missingIDs) == 0:
    print("No followup jobs needed, all finished!")
else:
    print(str(thisID) + " jobs had been submitted, of which " + str(len(missingIDs)) + " need to be resubmitted!") 

    missingstring = ""
    for missingID in missingIDs: missingstring += " " + str(missingID)

    # next, lets create a new submit file
    # in this new file, we need to replace two things:
    #   $(Process) to $(jobid)
    with open(args.previousSubmitFile, 'r') as file :
        filedata = file.read()

    filedata = filedata.replace('$(Process)', '$(jobid)')

    with open(args.submitFile, 'w') as file:
        file.write(filedata)

    # then we need to alter the submit command
    with open(args.submitFile, 'r') as file:
        lines = file.readlines()
        lines = lines[:-1]
        lines.append("queue 1 jobid in" + missingstring + "\n")

    with open(args.submitFile, 'w') as file:
        file.writelines(lines)