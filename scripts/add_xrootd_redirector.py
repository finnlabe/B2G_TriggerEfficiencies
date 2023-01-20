import sys

# we'll get the info what to do from the console inputs

if not len(sys.argv) == 3:
    raise Exception("Please specify exactly two arguments: the input file you want to edit, and the redirector to be used.")

inputfile = str(sys.argv[1])
redirector = str(sys.argv[2])

result = []

with open(inputfile, "r") as in_file:
    for line in in_file: result.append(redirector + line)

with open(inputfile, "w") as out_file:
    for line in result: out_file.write(line)
