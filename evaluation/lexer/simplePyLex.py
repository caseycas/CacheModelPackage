import sys
import os
from folderManager import Folder
from unicodeManager import UnicodeWriter
from utilities import *
from fileUtilities import *
from pygments.lexers import get_lexer_for_filename
from pygments import lex
from subprocess import call
import Android
import re
import dictUtils
import pickle

METADATAFLAG = True
SKIP_BIG = False
EXPLICIT_TYPE_WRITE = False

#File Level Entropy options:
#0) Original filePath
#1) Average line length
#2) LOC
#3) Total tokens
#4) And More...
def writeMetaData(outputDir, fileExtension, mdTokens, fileid, filePath, basePath, start_loc, lineCount, ave, lineDict, lineLengths):
    #print(EXPLICIT_TYPE_WRITE)
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
def writeLexedFile(outputDir, fileExtension, lexedWoComments, fileid, flag, explicitWrite):
    #print(lexedWoComments)
    assert(len(lexedWoComments) <= MAX_SIZE)
    #Uncomment if you want to copy the actual java file too.
    #Commented out to save space.
    #call(["cp", path, outputDir + "/" + str(i) + "." + fileExtension[2:]])
    # Write to file
    #Output format must be single line and be the input file name + .tokens.
    with open(outputDir + "/" + str(fileid) + "." + fileExtension[2:] + ".tokens", "wb") as outputFile:
        writer = UnicodeWriter(outputFile)
        for t in lexedWoComments:
            token = t[1]
            noWS = token.strip()
            noWS = noWS.replace('\n', '') #Remove new lines
            noWS = noWS.replace(' ', '_') #Replace any remaining internal spaces
            if(noWS == ""):
                continue
            #if((t[0] != Token.Literal.String) and "." in noWS):
            #    noWS = " ".join(re.split("(\.)", noWS)).strip()

            if(flag == "labelled" or flag == "android" or flag == "api"):
                if(explicitWrite == True):
                    noWS = "<" + noWS + "|" + str(t[0]) + ">"
            #if(flag == "labelled" or flag == "android"):
            #    if(t[0] == Token.Name.Namespace):
            #        noWS = convertNamespaceToken(noWS, "Token.Name.Namespace")
            #    elif(t[0] == Android.Namespace):
            #        noWS = convertNamespaceToken(noWS, "Android.Namespace")
            #    else:
            #        noWS = "<" + noWS + "|" + str(t[0]) + ">"
            #elif(flag == "name"):
            #    noWS = noWS.replace('.', '')
            outputFile.write(noWS.encode("utf-8"))
            #outputFile.write(noWS)
            outputFile.write(' ')
        outputFile.write('\n') #Without a new line between each file, there can be a problem with the SRILM ngram tools?


if len(sys.argv) < 8:
    print('Usage: python lex.py path_to_code_folder file_name_extension output_directory flag token_split skip_big explicit_type')
    print("Example: python simplePyLex.py ~/CodeNLP/HaskellProjects/ *.hs tests/ 0 full True False")
    print("Flag is 0, 1, 2, or 3 currently")
    print("0 -> replace all spaces in strings with _")
    print("1 -> replace all strings with a <str> tag.")
    print("2 -> add spaces to the ends of the strings")
    print("3 -> collapse strings to <str> and collapses numbers to a type as well.")
    print("token_split is full, keyword, name, labelled, nonname, android, api, or collapsed currently")
    print("labelled keeps all tokens, but attaches labels or name, keyword, or other")
    print("the android option is exclusively for android, and attaches a Android.* to")
    print("All android api references.  Other tokens retain the type from the highlighter.")
    print("Collapsed replaces all the name types (plus Keyword.Type) with their label.")
    print("Collapsed option also forces the string option to 1.")
    print("And finally two y/n options on whether to keep files with over " + str(MAX_SIZE))
    print("tokens and if we want to explicitly have the type <Token|Type> in the output files.")

    quit()

print(sys.argv)

# Path to root folder containing the source code
basePath = os.path.abspath(sys.argv[1])
codeFolder = Folder(basePath)


#print(codeFolder)

# File type to be considered
fileExtension = sys.argv[2]

# Path to output file with tokenized code
outputDir = sys.argv[3]
#outputFile = open(os.path.abspath(sys.argv[3]), 'wb')
#writer = UnicodeWriter(outputFile)

#String flag
strFlag = int(sys.argv[4])

token_split = sys.argv[5]


if(sys.argv[6].lower() == "true"):
    SKIP_BIG = True
else:
    SKIP_BIG = False


if(sys.argv[7].lower() == "true"):
    EXPLICIT_TYPE_WRITE = True
else:
    EXPLICIT_TYPE_WRITE = False

#Project -> file mapping
projectFiles = {} #String -> #List of Strings
#Functions defined in this corpus
corpusDefintions = {}

#Count of Error tokens
errorCount = 0

if(token_split.lower() == "api"):
    #Load in internally defined functions
    corpusDefinitions = pickle.load(open(os.path.join(basePath, "definitions.pickle"), 'r'))

i = 0

fileList = codeFolder.fullFileNames(fileExtension, recursive=False)
if(fileExtension == "*.c"): #For c, check for header files too.
    fileList += codeFolder.fullFileNames("*.h", recursive=False)
#Each top - level directory corresponds to a project.
for path in fileList:
    print(path)
    #print("In Loop!")
    try:
    #if(True):
        #print("Path: " + path)
        #fileContents = ""
        components = path.split(".")
        fileContents = ""
        #Minimized Javascript files require some preprocessing to estimate where the new lines were
        #if(len(components) >= 3 and components[-2].lower() == "min" and components[-1].lower() == "js"):
        #    fileContents = preprocessJSMinFile(path)
        #else:
        fileContents = ''.join(open(path, 'r').readlines())
        #lineCount = 0
        #with open(path, 'r') as f:
        #    for line in f:
        #        lineCount += 1
        #        fileContents += ''.join(line) 
        lexer = get_lexer_for_filename(path)
        tokens = lex(fileContents, lexer) # returns a generator of tuples
        tokensList = list(tokens)
        language = languageForLexer(lexer)
        (curProject, curFile) = getProjectAndFilename(path, basePath)

        # Strip comments and alter strings
        lexedWoComments = tokensExceptTokenType(tokensList, Token.Comment)
        lexedWoComments = tokensExceptTokenType(lexedWoComments, Token.Literal.String.Doc)
        beforeError = len(lexedWoComments)
        #Remove Things than didn't lex properly
        lexedWoComments = tokensExceptTokenType(lexedWoComments, Token.Error)
        errorCount += beforeError - len(lexedWoComments)

        #if(language == "Javascript"):
        #    lexedWoComments = mergeDollarSign(lexedWoComments)

        lexedWoComments = fixTypes(lexedWoComments, language) #Alter the pygments lexer types to be more comparable between our languages
        lexedWoComments = convertNamespaceTokens(lexedWoComments, language)
        
        if(token_split.lower() == "full" or token_split.lower() == "labelled" or token_split.lower() == "android" or token_split.lower() == "api"):
            if(strFlag == 0):
                lexedWoComments = modifyStrings(lexedWoComments, underscoreString)
            elif(strFlag == 1):
                lexedWoComments = modifyStrings(lexedWoComments, singleStringToken)
            elif(strFlag == 2):
                lexedWoComments = modifyStrings(lexedWoComments, spaceString)
            elif(strFlag == 3):
                lexedWoComments = modifyStrings(lexedWoComments, singleStringToken)
                #print(lexedWoComments)
                lexedWoComments = collapseStrings(lexedWoComments)
                lexedWoComments = modifyNumbers(lexedWoComments, singleNumberToken)
            else:
                print("Not a valid string handling flag. Valid types are currently 0, 1, 2, and 3")
                quit()

            if(token_split.lower() == "android"):
                lexedWoComments = labelAndroidTypes(lexedWoComments)

        elif(token_split.lower() == "keyword"):            
            lexedWoComments = getKeywords(lexedWoComments, language.lower())
        elif(token_split.lower() == "name"):
            lexedWoComments = getNameTypes(lexedWoComments, language.lower())
        elif(token_split.lower() == "nonname"):
            lexedWoComments = getNonNameTypes(lexedWoComments)
        elif(token_split.lower() == "collapsed"):
            lexedWoComments = modifyStrings(lexedWoComments, singleStringToken)
            lexedWoComments = collapseStrings(lexedWoComments)
            lexedWoComments = modifyNumbers(lexedWoComments, singleNumberToken)
            lexedWoComments = modifyNames(lexedWoComments, singleNameToken)
        else:
            print("Not a valid token split.")
            
        #Remove empty files (all comments).
        if(len(lexedWoComments) == 0):
            print("Skipping: " + path)
            continue

        
        (lineCount, ave, lineDict, lineLengths) = getLineMetrics(lexedWoComments)
        #print(lexedTokens)
        noWSTokens = []
        for t in lexedWoComments:
            noWS = t[1].strip()
            noWS = noWS.replace('\n', '') #Remove new lines
            if(noWS == "" or noWS[0] == Token.Text):
                continue
            noWSTokens.append((t[0],noWS))

        #noWSTokens = lexedWoComments #Experiment on spacing. Didn't seem to matter if newlines were included.

        #This needs to come after the whitespace tokens are removed for our sequence matching to work.
        if(token_split.lower() == "api"):
            #Load in internally defined functions
            ourFunctions = [x[1] for x in corpusDefinitions[curProject]] #Get the bag of function names defined in this project
            noWSTokens = relabelFunctions(noWSTokens, ourFunctions, language)

        #print(noWSTokens)
        #print(len(noWSTokens))

        skip = False
        #If over max size, break into chunks of approximately MAX_SIZE at  new lines
        if(not SKIP_BIG and len(noWSTokens) > MAX_SIZE):
            print("Big file: " + path)
            #print("Lines: " + str(lineCount))
            #print(lineLengths)
            #print(lineDict)
            #SPLIT into chunks of less than MAX_SIZE with each sub file being at least ending in a complete
            #line.
            startIndex = 0
            endIndex = 0
            lastIndex = 0
            
            while(len(noWSTokens[startIndex:]) > MAX_SIZE):
                print("Piece ID: " + str(i))
                #print(lastIndex)
                endIndex = getLastNewLine(noWSTokens, lineDict, startIndex) # What if this is bigger than MAX_SIZE?
                #print("Start: " + str(startIndex))
                #print("End: " + str(endIndex))
                if(endIndex <= startIndex or endIndex+1-startIndex > MAX_SIZE): #Not catching some...
                    print("Aberrant File, enormously long line. Discarding.")
                    skip = True
                    break
                    
                #endIndex = getLastNewLine(noWSTokens, startIndex) #This is broken now :(
                print(endIndex)
                dictUtils.addToDictList(projectFiles ,curProject,  outputDir + "/" + str(i) + "." + fileExtension[2:] + ".tokens")

                print("Printing: " + str(len(noWSTokens[startIndex:endIndex+1])) + " tokens.")
                if(METADATAFLAG):
                    lastIndex = writeMetaData(outputDir, fileExtension, noWSTokens[startIndex:endIndex+1], i, path, basePath, lastIndex, lineCount, ave, lineDict, lineLengths)
                writeLexedFile(outputDir, fileExtension, noWSTokens[startIndex:endIndex+1], i, token_split, EXPLICIT_TYPE_WRITE)
                i += 1
                startIndex = endIndex + 1 #Start of the new file one past the end.

            #Write out the last bit
            if(not skip):
                dictUtils.addToDictList(projectFiles ,curProject,  outputDir + "/" + str(i) + "." + fileExtension[2:] + ".tokens")
                if(METADATAFLAG):
                    writeMetaData(outputDir, fileExtension, noWSTokens[startIndex:], i, path, basePath, lastIndex, lineCount, ave, lineDict, lineLengths)
                writeLexedFile(outputDir, fileExtension, noWSTokens[startIndex:], i, token_split, EXPLICIT_TYPE_WRITE)
        elif(len(noWSTokens) <= MAX_SIZE):
            print("Normal File: " + path)
            dictUtils.addToDictList(projectFiles ,curProject,  outputDir + "/" + str(i) + "." + fileExtension[2:] + ".tokens")
            if(METADATAFLAG):
                writeMetaData(outputDir, fileExtension, noWSTokens, i, path, basePath, 0, lineCount, ave, lineDict, lineLengths)
            writeLexedFile(outputDir, fileExtension, noWSTokens, i, token_split, EXPLICIT_TYPE_WRITE)


        #Increment output file count
        if(not skip):
            i += 1
        else:
            skip = False
    except:
        print('Failed:', path)

#Write out the mapping from projects to files.
#Put this in the directory above the rest of the files.
if(outputDir.endswith("/")):
    aboveOutputDir = "/".join(outputDir.split("/")[0:-2]) 
else:
    aboveOutputDir = "/".join(outputDir.split("/")[0:-1])
pickle.dump(projectFiles, open(aboveOutputDir + "/project_file_map.pickle", "w"))
print(projectFiles)
print("Token.Error in this corpus: " + str(errorCount))
