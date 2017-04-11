import sys
import os
import argparse
import Android
import re
import pickle

from lexerFileManagement import *


"""
Another lexer for source code designed to put it in the format
expected by tensorflow lstms.
Requirements: Handles code and natural language (starting with 
Java and English)
Replaces values with <UNK> (needs two passes) that fall outside
the main vocabulary, using a frequency cut off determined by
vocabulary size argument.
Goal is to keep it cleaner than simplePyLex became.
"""


parser = argparse.ArgumentParser(description="Lexer to convert corpora into a " +
                                  "tensorflow lstm friendly form.") 
parser.add_argument("input_dir",help = "Top level directory of project/" + 
                     "data directory.  Will process all files recursively down " + 
                     "from here.", action="store", type=str)
parser.add_argument("ext", help = "A regular expression for the extension"+
                     " of all files to process (e.g. *.java for all java files)."+
                     "If you have files of this type in your current directory, "+
                     "you can send the ext in surrounded by quotes, e.g. "+ 
                     "\"*.txt\" will be needed to avoided selecting " + 
                     "stopwords.txt in your shell.",
                     action="store", type = str)
parser.add_argument("output_dir", help = "The output directory where the" +
                     " results are stored.", action = "store", type = str)
parser.add_argument("collapse_type", help = "0,1,2,3,4 whether to " + 
                     "replace all strings with <str>, space the \"'s out, to "+ 
                     "collpase strings to <str> and numbers to a shrunken type"+
                     " <int>, <float>, etc.",action= "store", type  = int)
parser.add_argument("token_split", help = "What special modifications " +
                     "to make to the output [full, name]. Full reports the " +
                     "text as is.  Name removes stopwords and punctuation.",
                     action = "store", type = str)
parser.add_argument("max_vocab", help = "Maximum vocabulary size" +
                     "if < 0, we have an unlimited vocab size and replace" +
                     "nothing with <UNK>.", type = int)
parser.add_argument("corpus_fraction", help = "What percentage of the files" +
                    "do we include in the training, validation, and test sets."+
                    "Used to create corpora of comparable sizes if one is " +
                    "significantly larger than another. This is used only " +
                    "for cases where --tri_split is enabled.", 
                    action = "store",type = float, default = 1.0)
parser.add_argument("--tri_split", help = "Final output is stored in " +
                    " train/test/validation sets, with sizes determined "+ 
                    "by the values in ttv_splits in clConfig.py. When false"
                    "creates only one to one file maps.", action = "store_true")
parser.add_argument("--metadata", help = "Create a type information file " +
                    "for each lexed file. Note that we always create a map of" +
                    "file ids used to create the train/test/and validation " +
                    "sets, and the mapping of the file ideas to their original"+
                    "locations.", action = "store_true")
parser.add_argument("--crossproject", help = "Only valid if we have --trisplit"+
                    " enabled, otherwise ignore it.  If that is true and we "+
                    "are lexing from source code projects, make sure that the"+
                    "choice of test files are distinct projects from the " +
                    "training set. That is, we randomly split our test set "+
                    "on the project rather than the file level.", 
                    action = "store_true")

args = parser.parse_args()

args.ext = args.ext.replace("\"", "") #Remove quotes

print("Ding!")

basePath = os.path.abspath(args.input_dir)

#Project -> file mapping
projectFiles = {} #String -> #List of Strings
#Functions defined in this corpus
corpusDefintions = {}
#counts of words
vocabulary = {}

#Count of Error tokens
errorCount = 0

fileList = getFilesToLex(basePath, args.ext)
print(fileList[0:5])
print(len(fileList))


if(args.ext in TREE_TEXTS):
    (vocabulary, projectFiles, i) = \
        ProcessTreeCorpus(basePath, args, vocabulary, projectFiles)
elif(args.ext in NATURAL_LANGUAGE_EXTS):
    (vocabulary, projectFiles, i) = \
        ProcessNLCorpus(basePath, args, vocabulary, projectFiles)
else:
    (vocabulary, projectFiles, i) = ProcessCodeCorpus(fileList, basePath, 
                                                   errorCount, args,
                                                   vocabulary, projectFiles)   

maxID = i-1
if(args.ext in NATURAL_LANGUAGE_EXTS):
    out_ext = ".txt.tokens"
elif(args.ext not in TREE_TEXTS):
    out_ext = "." + args.ext[2:] + ".tokens"
else: out_ext = "." + args.ext[2:]

#Perform the vocabulary cutoff
print(len(vocabulary))
if(len(vocabulary) > args.max_vocab):
    non_unk = vocabCutoff(vocabulary, args.max_vocab)
    #Rewrite all files with UNK
    for fileID in range(0, maxID):
        replaceWithUNK(non_unk, args.output_dir, fileID, out_ext)

#Record mapping to original files and projects.
#if(args.output_dir.endswith("/")):
#    aboveOutputDir = "/".join(args.output_dir.split("/")[0:-2]) 
#else:
#    aboveOutputDir = "/".join(args.output_dir.split("/")[0:-1])
#pickle.dump(projectFiles, open(aboveOutputDir + "/project_file_map.pickle", "w"))
pickle.dump(projectFiles, open("project_file_map.pickle", "w"))


if(args.tri_split):
    createTriSplitCorpus(maxID,args,vocabulary,out_ext, 
                         projectFiles,args.corpus_fraction,args.crossproject)