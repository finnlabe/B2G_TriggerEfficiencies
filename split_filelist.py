import sys

# we'll get the info what to do from the console inputs

if not len(sys.argv) == 4:
    raise Exception("Please specify exactly three arguments: the input files, the desired number of jobs and the output folder!")

inputfile = str(sys.argv[1])
njobs = int(sys.argv[2])
outputfolder = str(sys.argv[3])

file = open(inputfile, "r")
content_list = file.readlines()
file.close()

returnlist = []
for line in content_list:
    returnlist.append(line[:-1])
    
Ninputfiles = len(returnlist)

print("Found "+str(Ninputfiles)+" input files.")
print("Splitting into "+str(njobs)+" jobs...")

files_per_job = int(Ninputfiles/njobs-1)

print("This is "+str(files_per_job)+" maximum files per job.")

resultlist = []

for jobindex in range(njobs-1):
    
    result = ''
    
    for i in range(files_per_job):
        result += returnlist[jobindex*files_per_job + i]
        result += '\n'
                
    resultlist.append(result)
    
# last missing few files here
result = ''
    
for j in range( (njobs-1) * files_per_job, Ninputfiles ):
    result += returnlist[j]
    result += '\n'
            
resultlist.append(result)

# writing to file
resultindex = 0
for result in resultlist:
    f = open(outputfolder+"/filelist_"+str(resultindex)+".txt", "w")
    f.write(result)
    f.close()
    resultindex += 1