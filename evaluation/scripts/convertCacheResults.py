import sys
import os

DATA_LOC = "./data/" #This is kind of fragile, I should handle it more robustly

#The purpose of this script is to convert files with dumps
#of the output of Zhaopeng's cache model into a csv files
#that can be loaded easily into an R dataframe

#The format of the output file should be 1 column for each
#10-fold cross entropy.  The title of that column will be
#as follows: <project><NgramOrder><Cache/NoCache>[CacheOrder]
#[] -> optional, only if we used a cache

#Give a set of 10 entropies and fold numbers (paired), reorder according to the folds.
def reorderEntropies(ent, folds):
    newEnt = ["NA", "NA", "NA", "NA", "NA","NA", "NA", "NA", "NA", "NA"]
    i = 0
    for index in folds:
        newEnt[index] = ent[i]
        i += 1

    return newEnt


#file -> (str, list of 10)
#Give an single entropy results file, return a tuple with the name and the entropies
def parseFile(f):
    entropies = []
    foldNums = []
    hasCache = False
    project = ""
    order = 0
    lastSeenNum = -1
    unordered = False

    for line in f:
        print(line)
        if (line.startswith("Ngram File:")): #Get name + general ngram order
            project = os.path.split(line.replace("Ngram File:", "").strip())[-2].split("/")[-1]
            temp = line.split(" ")
            order = int(temp[len(temp)-1])
        elif (line.startswith("Cache: ")): #Determine if we have a cache and what the order is
            temp = line.replace(",","").split(" ")
            if(int(temp[1]) == 1): #Cache
                hasCache = True
                cacheOrder = int(temp[3])
            else:
                hasCache = False
        elif (line.startswith("Entropy:")):
            #print(lastSeenNum)
            if(lastSeenNum != -1 and lastSeenNum not in foldNums):
                unordered = True
                print("Sorry, the final csv summary table can't match each")
                print("test set's entropy to its exact fold.  This is due")
                print("to a parallel write conflict.  The table therefore")
                print("will not represent the entropies in fold order.")
            #assert(lastSeenNum != -1 and lastSeenNum not in foldNums)
            foldNums.append(lastSeenNum)
            lastSeenNum = -1
            entropies.append(float(line.strip().split(" ")[1]))
            #print(entropies[-1])
        elif (line.startswith(DATA_LOC)):# line.startswith("/home/ccasal")):
            temp = line.split("/")[-1]
            lastSeenNum = int(temp[4:5])
        else: #Ignore
            continue


    if(hasCache):
        name = project + str(order) + "Cache" + str(cacheOrder)
    else:
        name = project + str(order) + "NoCache"

    #Sometimes some of the test files don't copy into the combined output properly
    #when invoked via shell script.  I've never seen this happen manually, so I don't
    #know what the cause is.
    while len(entropies) < 10:
        entropies.append("NA")

    #Reorder the entropies.
    if(unordered == False):
        entropies = reorderEntropies(entropies, foldNums)

    print(entropies)
    return (name, entropies)


try:
    inputDir = sys.argv[1]
    outputFile = sys.argv[2]
except:
    print("usage: python convertCacheResults.py inputDir outputFile")
    quit()

columns = []

for filename in sorted(os.listdir(inputDir)): #Listing them in order makes making plots easier
    if(filename.endswith(".txt")):
        print(filename)
        f = open(inputDir + "/" + filename, 'r')
        columns.append(parseFile(f))

with open(outputFile, 'w') as f:
    #Write header
    first = True
    for col in columns:
        if(first):
            first = False
            f.write(col[0])
        else:
            f.write("," + col[0])
    f.write("\n")
    #Write data (this is somewhat awkwardly oriented)
    for i in range(0,10):
        first = True
        for col in columns:
            if(first):
                first = False
                f.write(str(col[1][i]))
            else:
                f.write("," + str(col[1][i]))

        f.write("\n")



