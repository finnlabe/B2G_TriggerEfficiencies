import sys

# we'll get the info what to do from the console inputs

if not len(sys.argv) == 4:
    raise Exception("Please specify exactly three arguments: the input files, the desired number of jobs and the output folder!")

inputfile = str(sys.argv[1])
njobs = int(sys.argv[2])
outputfolder = str(sys.argv[3])

# checking if output folder exists, if not, its created
if not os.path.exists(outputfolder):
    print("Creating output directory...")
    os.makedirs(outputfolder)

file = open(inputfile, "r")
content_list = file.readlines()
file.close()

returnlist = []
for line in content_list:
    returnlist.append(line[:-1])
    
Ninputfiles = len(returnlist)

print("Found "+str(Ninputfiles)+" input files.")
print("Splitting into "+str(njobs)+" jobs...")

files_per_job = int(Ninputfiles/njobs)

if(Ninputfiles % njobs == 0): print("This is "+str(files_per_job)+" maximum files per job.")
else: print("This is "+str(files_per_job+1)+" maximum files per job.")


resultlist = []

for jobindex in range(njobs):
        
    files_for_this_job = files_per_job
    if(jobindex < Ninputfiles % njobs): files_for_this_job += 1

    result = ''

    for i in range(files_for_this_job):
        
        result += returnlist[jobindex*files_per_job + i]
        result += '\n'
                
    resultlist.append(result)

# writing to file
resultindex = 0
for result in resultlist:
    f = open(outputfolder+"/filelist_"+str(resultindex)+".txt", "w")
    f.write(result)
    f.close()
    resultindex += 1