from os import listdir
from os.path import isfile,join
import random
import sys
import subprocess
PIPE = subprocess.PIPE

#Reduce the files considered in a project to a subset of them.
def selectRandomSubsample(baseList, fractionSampled):
    sampleSize = int(len(baseList)*fractionSampled)
    #Get random sample of a list for python: credit to answer on this question: 
    #http://stackoverflow.com/questions/6482889/get-random-sample-from-list-while-maintaining-ordering-of-items
    subSample = [baseList[i] for i in sorted(random.sample(xrange(len(baseList)), sampleSize)) ]
    return subSample


try:
    input_dir = sys.argv[1]
    sample = float(sys.argv[2])
    output_dir = sys.argv[3]
except:
    print "usage: python input_dir sample_size output_dir"
    quit()

files = [f for f in listdir(input_dir) if isfile(join(input_dir, f))]
print(files)

samplefiles = selectRandomSubsample(files, sample)

i = 0
for next_file in samplefiles:
    command = ["cp", input_dir + "/" + next_file, output_dir + "/" + str(i) + ".rb.tokens"]
    print(command)
    proc = subprocess.Popen(command, stderr=PIPE, stdout=PIPE)
    out,err = proc.communicate()
    if(not proc.returncode):
        print("copy error: " + str(command))
        print(err)
        print(out)
    
    i += 1