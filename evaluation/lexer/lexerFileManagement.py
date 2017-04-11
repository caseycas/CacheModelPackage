'''
Helper functions to manage file and directory information for the 
cleanLexer.py
'''
import sys
import os
import random
from lexerModHelper import *
from lexerNLHelper import *
from dictUtils import *
from folderManager import Folder
from fileUtilities import *
from clConfig import *


def ProcessTreeCorpus(basePath, args, vocabulary, reindexMap):
    """
    Process a corpus of ast or constituency parse files.
    """
    i = 0
    nltk_ext = "." + args.ext

    corpus = nltk.corpus.PlaintextCorpusReader(basePath, nltk_ext) 
    #,word_tokenizer=nltk.tokenize.regexp.WhitespaceTokenizer())

    for fileid in corpus.fileids():
        #if(i > 1000):
        #    break
        print(str(i) + ":" + fileid)
        if(True):
        #try:
            print(fileid)
            #REDO
            (vocabulary) = ProcessTreeFile(corpus, basePath, args, 
                                           fileid, i, vocabulary)
            reindexMap[str(i) + ".tokens"] = fileid
            i += 1
        #except:
        #    print("Error - skipping " + str(fileid))
        #    print("Is this file empty?")

    return(vocabulary, reindexMap, i)

def ProcessTreeFile(corpus, basePath, args, inputfile, fileid, vocabulary):
    """
    Process a tree based file like the files from a Java AST or a 
    English constituency parse.

    Parameters:
    -----------
    corpus - an nltk corpus object
    basePath - the path of the upper level directory being processed
    args - the arg parse object storing all user options.
    inputfile - the local name of the input file
    fileid - the unique identifier for the lexed output
    vocabulary - a map of token -> count
    projectFiles - a map tracing what project the output files originally 
    came from. 

    Returns:
    --------
    vocabulary - the map of token counts we are updating.

    """

    words = corpus.words(os.path.join(basePath, inputfile))
    ext = args.ext[1:]
    if(".tokens" not in ext):
        ext += ".tokens"

    with open(os.path.join(args.output_dir, 
                           str(fileid) + ext), "w") as outputFile:

        for w in words:
            #print(w)
            #w = w.strip().replace('\n', '')
            w = w.replace("\"", "<QUOTE>")
            if(w.strip() == ""):
                continue

            #Update vocabulary
            vocabulary = addToDictCount(vocabulary, w.strip())

            outputFile.write(w.encode('utf8'))
            outputFile.write(' ')

        #Without a new line between each file, there can be a problem
        #with the SRILM ngram tools?
        outputFile.write(' \n') 

    return(vocabulary)

def ProcessCodeCorpus(fileList, basePath, 
                      errorCount, args,
                      vocabulary, projectFiles):
    """
    Process a corpus of source code files.

    Parameters:
    ----------
    Returns:
    --------
    """
    i = 0
    for path in fileList:
        #if(i > 1000):
        #    break
        print(str(i) + ":" + path)
        #try:
        if(True):
            (vocabulary, projectFiles, status) = \
                ProcessCodeFile(path, basePath, errorCount, args, 
                                i, vocabulary, projectFiles)
            print(status)
            if(status):
                i += 1

    return(vocabulary, projectFiles, i)


def ProcessCodeFile(path, basePath, errorCount, args, 
                    fileid, vocabulary, projectFiles):
    """

    Process a source code file in the expected format.
    Parameters:
    -----------
    path - the path of the file being processed
    basePath - the path of the upper level directory being processed
    errorCount - an ongoing count of the number of Token.Errors 
    Pygments produces
    args - the arg parse object storing all user options.
    fileid - the unique identifier for the lexed output
    vocabulary - a map of token -> count
    projectFiles - a map tracing what project the output files originally 
    came from. 

    Returns:
    --------
    vocabulary - the map of token counts we are updating.
    projectFiles - a map of the projects that we are updating
    status - TRUE/FALSE - if FALSE, we are skipping this file, and shouldn't
    increment fileid.
    """
    (curProject, curFile, lexedWoComments, language, fileErrors) = \
            preprocessFile(path, basePath)

    errorCount += fileErrors
    
    #Move to function.
    if(args.token_split.lower() == "full"):
        lexedWoComments = collapseLiterals(args.collapse_type, lexedWoComments)
    elif(args.token_split.lower() == "name"):
        lexedWoComments = getNameTypes(lexedWoComments, language.lower())
        
    #Remove empty files (all comments).
    if(len(lexedWoComments) == 0):
        print("Skipping: " + path)
        return(vocabulary, projectFiles, False)

    (lineCount, ave, lineDict, lineLengths) = getLineMetrics(lexedWoComments)
    addToDictList(projectFiles, curProject, 
                    os.path.join(args.output_dir, str(fileid) + "." + 
                    args.ext[2:] + ".tokens"))
        
    #Function is bugged currently
    if(args.metadata):
        noWSTokens = []
        for t in lexedWoComments:
            noWS = t[1].strip()
            noWS = noWS.replace('\n', '') #Remove new lines
            if(noWS == "" or noWS[0] == Token.Text):
                continue
            noWSTokens.append((t[0],noWS))
        
        writeMetaData(args.output_dir, args.ext, noWSTokens, fileid, path, 
                      basePath, 0, lineCount, ave, lineDict, lineLengths)

    vocabulary = updateVocab(vocabulary, lexedWoComments)

    #print(lexedWoComments)
    writeLexedFile(args.output_dir, args.ext, lexedWoComments, fileid, False)

    return (vocabulary, projectFiles, True)

def ProcessNLCorpus(basePath, args, vocabulary, reindexMap):
    """
    Process a corpus of natural language files.
    """
    stopwords = []

    if(args.token_split == "name"):
        with open(stopwordsFile, 'r') as f:
            for line in f:
                stopwords.append(line.lower().strip())

    i = 0
    words = []
    first = True

    nltk_ext = "." + args.ext

    corpus = nltk.corpus.PlaintextCorpusReader(basePath, nltk_ext) 
    #,word_tokenizer=nltk.tokenize.regexp.WhitespaceTokenizer())

    for fileid in corpus.fileids():
        #if(i > 1000):
        #    break
        #if True:
        try:
            print(fileid)
            #REDO
            vocabulary = ProcessNLFile(corpus, basePath, fileid, i, 
                                       stopwords, vocabulary, args)
            reindexMap[str(i) + ".tokens"] = fileid
            i += 1
        except:
            print("Error - skipping " + str(fileid))
            print("Is this file empty?")

    return(vocabulary, reindexMap, i)


def ProcessNLFile(corpus, basePath, inputfile, fileid, stopwords, vocabulary, args):
    """
    Process a natural language file in the expected format.
    Currently only works with English and English variants.
    Want to store 1 sentence per line

    Parameters:
    -----------
    corpus - nltk file processing object.
    basePath - the path of the upper level directory being processed
    inputfile - the name of the source file
    fileid - the unique identifier for the lexed output
    stopwords - list of words to remove.
    vocabulary - a map of token -> count
    args - the arg parse object storing all user options.


    Returns:
    --------
    vocabulary - the map of token counts we are updating.

    """   
    sents = corpus.sents(os.path.join(basePath, inputfile))
    #elif(noStopwords == 2):
    #    words = removePunct(words)

    #punctKeep = 1

    with open(os.path.join(args.output_dir, 
                           str(fileid) + ".txt.tokens"), "w") as outputFile:

        #Place one sent per line.
        for words in sents:
            #print(words)
            #Start each line with a space.
            outputFile.write(' ')
            if(stopwords != []):
                words = filterStopwords(stopwords, words)
                
            #words = removePunct(words)
            for w in words:
                #print(w)
                #w = w.strip().replace('\n', '')
                w = w.replace("\"", "<QUOTE>")
                if(w.strip() == ""):
                    continue
                #Skip u_Pos stuff for now.
                #if(u_Pos == 1):
                #    if(w == "_"):
                #        continue
                #    if(w in punct):
                #        if(punctKeep == 1):
                #            punctKeep = 0
                #        else:
                #            punctKeep = 1
                #            continue
                #
                #    w = getPOSUnderscore(w)

                #Update vocabulary
                vocabulary = addToDictCount(vocabulary, w.strip())

                outputFile.write(w.encode('utf8'))
                outputFile.write(' ')

            #Without a new line between each file, there can be a problem
            #with the SRILM ngram tools?
            outputFile.write(' \n') 

    return(vocabulary)

def getFilesToLex(top_lvl_dir, extension):
    """
    Desc: Get all filepaths recursively from top_lvl_dir that
    match extension

    Parameters:
    ----------
    top_lvl_dir - a directory that is the head of a project or
    corpus.  We will recursively examine all files under it

    extension - A wildcard regex for the type of extension
    to collect (e.g. *.java)

    Returns:
    --------
    list of filepaths matching extension in top_lvl_dir and
    any subdirector of it.
    """

    # Path to root folder containing the source code
    basePath = os.path.abspath(top_lvl_dir)
    inputFolder = Folder(basePath)
    fileList = inputFolder.fullFileNames(extension, recursive=True)
    if(extension == "*.c"): #For c, check for header files too.
        fileList += inputFolder.fullFileNames("*.h", recursive=True)

    return fileList

def writeMetaData(outputDir, fileExtension, mdTokens, fileid, filePath, basePath, start_loc, lineCount, ave, lineDict, lineLengths):
    """
    Parameters:
    -----------
    outputDir
    fileExtension
    mdTokens
    fileid
    filePath
    basePath
    start_loc
    lineCount
    ave
    lineDict
    lineLengths
    Returns:
    --------
    """
    assert(len(mdTokens) <= len(lineDict))
    i = 0
    with open(outputDir + "/" + str(fileid) + "." + fileExtension[2:] + ".metadata", "w") as f:
        (project, file_name) = getProjectAndFilename(filePath, basePath)
        f.write(project + " " + file_name + "\n") #easier combining later on

        #NOTE: This gets line length with comments removed
        #(lineCount, ave, lineDict) = getLineMetrics(
        #(lineCount, ave, lineDict) = getLineMetrics(lexedTokens)
        if(lineCount == 0):
            print("Empty.")
            return

        #print(lineDict)
        #print(lineLengths)
        #quit()

        #f.write("Token Info: (type, token, location in file, location in line)\n")
        f.write("token,token_type,token_location,token_line,project,file_name,file_token_count,file_line_count, file_average_line_length, line_length\n")
        for token in mdTokens:
            noWS = token[1]
            noWS = noWS.replace(' ', '_') #Replace any remaining internal spaces
            #if((token[0] != Token.Literal.String) and "." in noWS):
            #    noWS = " ".join(re.split("(\.)", noWS)).strip()
            f.write("\"" + noWS.encode("utf-8") + "\"," + str(token[0]) + "," + str(i + start_loc) + "," + str(lineDict[i + start_loc]) + "," + project + "," + file_name + "," + str(len(lineDict)) + "," + str(lineCount) + "," + str(ave) + "," + str(lineLengths[lineDict[i + start_loc]]) + "\n")
            
            i += 1

    #print("Start Loc: " + str(start_loc))
    #print("I: " + str(i))
    return start_loc + i
    


#string, string, list of tokens, int, string --> -----
#Given the output directory, the original file type, the tokens to write, and the
#file id, write out the tokens to file
#Precondition: files must be less than MAX_SIZE tokens (large files seem to
#cause problems with Zhaopeng's cache model.
def writeLexedFile(outputDir, fileExtension, tokens, fileid, removeWS):
    """
    Write out the words of the token list to a file in the output directory.

    Parameters:
    -----------
    outputDir - the output directory

    fileExtension - the extension regular expression used to capture the 
    input file that produced this (e.g. *.java)

    tokens - the Pygments list of tuples (token_type, token)

    fileid - a unique number referring to this file's name ID for future
    scripts.

    removeWS - Remove all whitespace and collapse everything onto a single line?
    Returns:
    -----------
    """

    with open(outputDir + "/" + str(fileid) + "." + fileExtension[2:] + 
                ".tokens", "wb") as outputFile:
        #writer = UnicodeWriter(outputFile)
        lastToken = ""
        outputFile.write(' ')
        for t in tokens:
            token = t[1]
            if(removeWS):
                noWS = token.strip()
                noWS = noWS.replace('\n', '') #Remove new lines
                #Replace any remaining internal spaces
                noWS = noWS.replace(' ', '_')
                if(noWS == ""):
                    continue
                outputFile.write(noWS.encode("utf-8"))
                #Without a new line between each file, there can be a problem 
                #with the SRILM ngram tools?
                outputFile.write(' \n') 
            else:    
                if(token.count('\n') > 1 and token.strip() == ""):
                    outputFile.write(" \n")
                    outputFile.write(' ')
                elif(not ("\n" in lastToken and token.strip() == "")): #skip blank lines
                    outputFile.write(token.encode("utf-8"))
                    outputFile.write(' ')

            lastToken = token

def replaceToken(token, non_unk_list):
    """
    Replace tokens with UNK
    """
    if(token == "UNK"):
        return "<unk>"

    if(token in non_unk_list):
        return token
    else:
        return "<unk>"

def UNKExt(oldExt):
    return oldExt[:oldExt.rfind(".")] + ".unk" + oldExt[oldExt.rfind("."):]

def replaceWithUNK(non_unk, file_dir, fileID, ext):
    """
    Create a new output file where the tokens not in non_unk are
    replaced with UNK token.  New file should have name similar to
    the old, but with an ending of no_unk.tokens.

    Parameters:
    ----------
    non_unk - set of vocabulary words
    dir - directory of the output file
    fileID - ID of the output file
    extensions - extension of the output file
    Returns:
    --------
    """
    newExt = UNKExt(ext)
    with open(os.path.join(file_dir, str(fileID) + ext), "r") as in_file:
        with open(os.path.join(file_dir, str(fileID) + newExt), 'w') as out_file:

        
            for line in in_file:
                tokens = line.split()
                tokens = [replaceToken(t, non_unk) for t in tokens]
                out_file.write(" ".join(tokens) + "\n")

#Reduce the files considered in a project to a subset of them.
def selectRandomSubsample(baseList, fractionSampled):
    sampleSize = int(len(baseList)*fractionSampled)
    #Get random sample of a list for python: credit to answer on this question: 
    #http://stackoverflow.com/questions/6482889/get-random-sample-from-list-while-maintaining-ordering-of-items
    subSample = [baseList[i] for i in sorted(random.sample(xrange(len(baseList)), sampleSize)) ]
    return subSample

def selectRandomSubsampleInt(baseList, sampleSize):
    print("Sample Size:" + str(sampleSize))
    print("To Sample Size: " + str(len(baseList)))
    #Get random sample of a list for python: credit to answer on this question: 
    #http://stackoverflow.com/questions/6482889/get-random-sample-from-list-while-maintaining-ordering-of-items
    subSample = [baseList[i] for i in sorted(random.sample(xrange(len(baseList)), sampleSize)) ]
    return subSample

def combineIDs(file_dir, ids, in_ext, use_unk, name):
    """
    Combine all the files in dir matching the combination
    of the id and the possibly modified extension into a
    file in the same directory called name
    Parameters:
    -----------
    file_dir - the directory where the files are stored and
    where we will save the results
    ids - a list of ids of the files in the directory
    in_ext - the extension of the ids
    use_unk - a boolean for if we should modify the out_ext
    by putting a ".unk" before the ".tokens"
    name - the name of the output file, typically "train",
    "test", or "validate"

    Returns:
    --------
    """
    
    if(use_unk):
        in_ext = UNKExt(in_ext)
    print("BEEP")
    with open(os.path.join(file_dir, name), 'w') as output_file:
        for file_id in ids:
            with open(os.path.join(file_dir, str(file_id) + in_ext), 'r') as in_file:
                #Do another removal of the blank lines...
                for line in in_file:
                    if(line.strip() == ""):
                        continue
                    #For some reason the first space is being removed
                    #I don't know why, so this is a bit of a hack fix.
                    line = line.strip()    
                    output_file.write(" " + line + " \n") 
                #output_file.write(in_file.read())


#Return a list of all files (IDs in /files) for a project based on a map 
#created by our lexer.
def getAllFilesInProjects(projectDict, keys):
    files_list = []
    for k in keys:
        pFiles = projectDict[k]
        files_list += pFiles

    out = list(set(files_list)) #I was having a duplication problem here somehow...
    #print("Files Grabbed: " + str(len(out)))
    return out

def getProjectSplits(projectCount):
    """
    Create counts of how many projects we will
    have in the training, test, and validation sets.
    We must have an even number of projects split
    between validation and testing.
    Returns:
    --------
    (Training size, validation size, test size) = all in # projects
    """
    train_base = int(splits["train"]*projectCount)
    if(projectCount - train_base % 2 != 0):
        train_base += 1
    
    other_size = int((projectCount - train_base)/2)

    return (train_base, other_size, other_size)

def balancedProjectSplit(project_to_file_map):
    print("Balanced Project Split.")
    #print(project_to_file_map)
    #quit()

    projects = project_to_file_map.keys()
    #Sort by size
    project_files = [(p, getAllFilesInProjects(project_to_file_map, [p])) for p in projects]
    #print(project_files[0][0])
    project_files = sorted(project_files, key = lambda pro: len(pro[1]), reverse = True)
    #for p in project_files:
    #    print(p[0])
    #quit()
    project_number = len(projects)
    print("Project count: " + str(project_number))
    assert(project_number >= 3) #Need at least 1 project in test, train and validate.
    (p_train, p_valid, p_test) = getProjectSplits(project_number)
    train = []
    validate = []
    test = []

    i = 0
    for project, files in projects_files.iteritems():
        if(i % 3 == 0):
            train += files
        elif(i % 3 == 1 and p_valid > 0):
            validate += files
            p_valid -= 1
        elif(i % 3 == 2 and p_test > 0):
            test += files
            p_test -= 1
        else:
            train += files

    return (train, valid, test)




def splitCounts(size):
    #Lookup split values
    train_count = int(size*splits["train"])
    test_count = int(size*splits["test"])
    validate_count = size - (train_count + test_count)
    print(str(train_count) + " " + str(test_count) + " " + str(validate_count))
    return(train_count, validate_count, test_count)

def selectRandomSplits(baseIDs):
    (train_count, validate_count, test_count) = splitCounts(len(baseIDs))
    train_sample = random.sample(baseIDs, train_count)
    left_over = list(set(baseIDs)-set(train_sample))
    test_sample = random.sample(left_over, test_count)
    validate_sample = list(set(left_over) - set(test_sample))
    return(train_sample, validate_sample, test_sample)

def createTriSplitCorpus(maxID,args,vocabulary,out_ext,projectFiles,subSample,crossProject):
    """
    Split the corpus into a training, testing,
    and validation corpus by combining random file IDs.
    Parameters:
    -----------
    maxID - the total number of fileIDs generated
    args - our Argparse command line arguments
    vocabulary - the recorded vocabulary
    out_ext - the extension used in our indivdual file outputs
    usually ".<language>.tokens"
    projectFiles - a mapping of file Ids to projects (only used if
    its not a natural language corpus, and crossProject is true)
    subSample - float between 0.0 and 1.0, what % of files do we want
    to keep.
    crossProject - do we split so that there are distinct projects
    in the train, validation, and test sets (true/false)
    """

    if(args.ext not in NATURAL_LANGUAGE_EXTS and crossProject):
        (train_sample, 
         validate_sample, 
         test_sample) = balancedProjectSplit(projectFiles)
    else:
        #Select the training data randomly
        (train_sample, 
         validate_sample, 
         test_sample) = selectRandomSplits(range(maxID))
        #train_sample = random.sample(range(maxID), train_count)
        #left_over = list(set(range(maxID))-set(train_sample))
        #test_sample = random.sample(left_over, test_count)
        #validate_sample = list(set(left_over) - set(test_sample))

    if(subSample < 1.0):
        train_sample = selectRandomSubsample(train_sample, subSample)
        validate_sample = selectRandomSubsample(validate_sample, subSample)
        test_sample = selectRandomSubsample(test_sample, subSample)

    train_sample = [str(t) for t in train_sample]
    test_sample = [str(t) for t in test_sample]
    validate_sample = [str(t) for t in validate_sample]
    #Combine these into a train, test, and validate file.
    use_unk = len(vocabulary) > args.max_vocab
    combineIDs(args.output_dir, train_sample, out_ext, 
               use_unk, "train")

    combineIDs(args.output_dir, test_sample, out_ext, 
               use_unk, "test")

    combineIDs(args.output_dir, validate_sample, out_ext, 
               use_unk, "valid")

    #Write out a map showing what IDs went into which set
    with open("split_map", "w") as f:
        f.write("Training: \n")
        f.write(" ".join(train_sample) +    "\n")
        f.write("Validation: \n")
        f.write(" ".join(validate_sample) + "\n")
        f.write("Testing: \n")
        f.write(" ".join(test_sample) + "\n")