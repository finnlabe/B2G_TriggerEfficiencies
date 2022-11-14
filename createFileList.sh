#!/bin/bash

if [ "$#" -eq "2" ]
    then
        echo "Creating filelist for $1 in $2."
        echo "If the output file is not filled, please activate your GRID proxy!"
        dasgoclient -query="file dataset=$1" > $2
    else
        echo "Please give two arguments, the DAS query and the desired output file!"
    fi

