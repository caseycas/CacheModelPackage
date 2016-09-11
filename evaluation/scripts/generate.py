'''
This is a wrapper script for the generate option of the completion script.
Takes command line input from the user, lexes it, and then forwards arguments
to the completion.
'''

import sys
import argparse
import subprocess
import subprocess
PIPE = subprocess.PIPE

parser = argparse.ArgumentParser(description="Wrapper script for calling the generate mode of completion.  Use for entering unlexed command line input.")
#Arg parse treats "..." as one argument.
parser.add_argument("input", help = "The java code to feed as a prefix for the language model. Surround with \"\"")
parser.add_argument("model", help = "The location of the .arpa file you want to use as your base language model.")
parser.add_argument("order", type=int, help = "The max order of ngrams you want to use")
parser.add_argument("tokens", type=int, help = "The number of tokens to generate after the entered text.")
parser.add_argument("language", help = "What language is this in? [\"txt\"/\"java\"/\"hs\"/\"rb\"/\"c\"\"h\"/\"cl\"]  Current supports english (txt), java (java), haskell (hs), ruby (rb), c (c/h), clojure (cl).  Others can be done, but you need to a lexer to properly separate the tokens or do it manually and call completion separately.")

args = parser.parse_args()

if(args.order <= 0):
    print("Ngram order must be positive.")
    quit()

if(args.tokens <= 0):
    print("Number of tokens to generate must be positive.")
    quit()

textPrefix = args.input

with open("temp." + args.language, 'w') as f:
    f.write(textPrefix)

newInput = ""

if(args.language == "txt"):
    #TODO Select English lexer.
    #python lexEnglish.py inputDir fileType outputDir filterStopwords [stopwordsFile]
    command = ["python", "./lexer/lexEnglish.py", "./", "temp.txt", "./", str(0)] #Right now it outputs just 0.tokens
    newInput = "0.tokens"
elif(args.language in ["java", "hs", "rb", "c", "h", "cl"]):
    #Lex the textPrefix and store in file.
    #freqDir.getAbsolutePath(), fT_lex_regex, freqDir.getAbsolutePath(), "0", "full", "True", "False"}
    command = ["python", "./lexer/simplePyLex.py", "./", "*." + args.language,  "./", "3", "full", "True", "False"]
    newInput = "0." + args.language + ".tokens"
else:
    print("Not a recognized language. Try generate.py -h and look at the \"language\" option documentation.")

print(command)
proc = subprocess.Popen(command, stderr=PIPE, stdout=PIPE)
_pc = proc.communicate()

#Call completion with correct arguments.
#./completion -INPUT_FILE test.txt -NGRAM_FILE data/java/fold0.train.3grams -NGRAM_ORDER 3 -GENERATE -GENCOUNT 2
#./completion -INPUT_FILE 0.java.tokens -NGRAM_FILE data/java/fold0.train.3grams -NGRAM_ORDER 3 -GENERATE -GENCOUNT 2
command = ["./completion", "-INPUT_FILE", newInput, "-NGRAM_FILE", args.model, "-NGRAM_ORDER", str(args.order), "-GENERATE", "-GENCOUNT", str(args.tokens)]
print(command)
proc = subprocess.Popen(command, stderr=PIPE, stdout=PIPE)
_pc = proc.communicate()

#Need to covert the output to something more intellible.
print(_pc[0])

#Clean up the temporary files
command = ["rm", "temp." + args.language]
proc = subprocess.Popen(command, stderr=PIPE, stdout=PIPE)
_pc = proc.communicate()

command = ["rm", "0.tokens", "0." + args.language + ".tokens", "0." + args.language + ".metadata"]
proc = subprocess.Popen(command, stderr=PIPE, stdout=PIPE)
_pc = proc.communicate()

command = ["rm", "0." + args.language + ".tokens"]
proc = subprocess.Popen(command, stderr=PIPE, stdout=PIPE)
_pc = proc.communicate()

command = ["rm", "0." + args.language + ".metadata"]
proc = subprocess.Popen(command, stderr=PIPE, stdout=PIPE)
_pc = proc.communicate()

command = ["rm", "project_file_map.pickle"]
proc = subprocess.Popen(command, stderr=PIPE, stdout=PIPE)
_pc = proc.communicate()