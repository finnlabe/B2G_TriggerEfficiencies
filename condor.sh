#!/bin/bash

if [ "$#" -eq "5" ]
    then
        # Check input and where we are
        export XRD_REQUESTTIMEOUT=1800
        echo "Input file list: $1"
        echo "Ref trigger file: $2"
        echo "Test trigger file: $3"
        echo "Era is: $4"
        echo "Job ID for naming: $5"

        # we should have all files copied to the work server using the condor submit script
        echo "Starting the root script"

        python runTriggerEfficiencies.py -i $1 -r $2 -t $3 -e $4

        echo "Condor job done, transferring outout..."
        
        # renaming output file according to job ID
        mv "output.root" "output_$5.root"
        
        # the transfer back will be done automatically by condor!

    else
        echo "Please give exactly five arguments!"
    fi




