README
Zhaopeng Tu
2014-07-23




1. Preprocess

You should extract all java files from the project, and do necessary preprocess: remvoe comments, tokenization. Go to the annotation folder, and run './walk.py':

./walk.py input_dir output_dir

The input_dir is the original project folder, and output is the folder that stores all tokenized codes. Generally, the output files are indexed by the number, and contains:

0.java         // the un-tokenized code without comments
0.java.lines   // the tokenized codes stored in lines
0.java.tokens  // the tokenized codes written in a single line (for training LM)

(If you try to deal with other programming languages, say C, modify the Lexer (LexJava-1.0.jar) in walk.py:

 19                 os.system('java -jar bin/LexJava-1.0.jar %s' % output))
)





2. Evaluation

After preprocessing, you should rename the output folder to "files" and put them in the "evaluation" folder. 

For example, mkdir a folder named "data" in "evaluation", and the structure is:
 | evaluation
     | data
         | sample_project
             | files    // this contains all processed files obtained from Step1



2.1 Training

The default setting is that we use 10-fold cross-validation for training (we split the files into 10 parts, then for each part, we train the language model from the other 9 parts, and test on the give part).

Usage:

./bin/train.py data/sample_project 3

Here "3" denotes the order of n-grams trained from the "sample_project". Here we use 3-grams.

You will find all the trained files in the "sample_project", whose structure is as following:
 
 | evaluation
     | data
         | sample_project
             | files    // this contains all processed files obtained from Step1
             fold0.test              // the test file list for fold0
             fold0.train.3grams      // the trained language model for fold0
             fold1.test
             fold1.train.3grams
             fold2.test
             fold2.train.3grams
             fold3.test
             fold3.train.3grams
             fold4.test
             fold4.train.3grams
             fold5.test
             fold5.train.3grams
             fold6.test
             fold6.train.3grams
             fold7.test
             fold7.train.3grams
             fold8.test
             fold8.train.3grams
             fold9.test
             fold9.train.3grams

Possible Troubles:
1. If you find the LM tools 'ngram' and 'ngram_count' cannot work on your machine. Try to download the latest version from the website 'http://www.speech.sri.com/projects/srilm/download.html', and compile it on your own machine. Replace the original ones with your compiled procedures.



2.1 Test

Try to find the full command list by typing "./completion".

    the necessary parameters: 
    ---------------------------------------------------------------
    -INPUT_FILE         the input file
    -NGRAM_FILE         the ngrams file
    -NGRAM_ORDER        the value of N (order of lm)
    ---------------------------------------------------------------

    the optional parameters:
    ---------------------------------------------------------------
    -ENTROPY            calculate the cross entropy of the test file
                        rather than providing the suggestions
    -TEST               test mode, no output, no debug information
    -FILES              test on files or not, default on a single file
    -DEBUG              output debug information
    -OUTPUT_FILE        the output file
    ---------------------------------------------------------------
    -BACKOFF            use the back-off technique
    -CACHE              use the cache technique 
    -CACHE_ONLY         only use the cache technique without ngrams
    -CACHE_ORDER        the maximum order of ngrams used in the cache (default: 3)
    -CACHE_DYNAMIC_LAMBDA   dynamic interpolation weight for -CACHE (H/(H+1)), default option
    -CACHE_LAMBDA       interpolation weight for -CACHE
    -WINDOW_CACHE       build the cache on a window of n tokens (default n=1000)
    -WINDOW_SIZE        the size of cache, default: 1000 tokens
    -FILE_CACHE         build the cache on a file or related files
    -SCOPE_FILE         the scope file for scope cache on CLASS or METHOD
    -RELATED_FILE       when using cache on file scope, build the cache on the related files
                        FILE_DIR should be given
    -FILE_DIR           the directory that stores all files
    ---------------------------------------------------------------


Try to find examples from "entropy.bat" and "suggestion.bat" for calculating entropies and code suggestion, respectively. 

