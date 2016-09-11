#include <iostream>

#include "data.h"
#include "suggestion.h"

using namespace std;

string copy_right = "\n\
=========================================================\n\
Author: Zhaopeng Tu\n\
 Email: tuzhaopeng@gmail.com\n\
  Date: 2013-11-18\n\
  Note: A Caching LM-based Code Suggestion Tool V0.3\n\
=========================================================\n";

string help_info = "\n\
you should enter the following parameters:\n\
the necessary parameters: \n\
---------------------------------------------------------------\n\
 -INPUT_FILE  \t\t the input file\n\
 -NGRAM_FILE  \t\t the ngrams file\n\
 -NGRAM_ORDER \t\t the value of N (order of lm)\n\
---------------------------------------------------------------\n\
\n\
the optional parameters:\n\
---------------------------------------------------------------\n\
-ENTROPY      \t\t calculate the cross entropy of the test file\n\
              \t\t rather than providing the suggestions\n\
-GENERATE     \t\t takes a string and generates text based on a model instead of on test set.\n\
-GENCOUNT     \t\t followed by an int, determines how many tokens we generate in generate mode\n\
              \t\t required when you have selected the -GENERATE option.\n\
-TEST         \t\t test mode, no output, no debug information\n\
-FILES        \t\t test on files or not, default on a single file\n\
-DEBUG        \t\t output debug information\n\
-OUTPUT_FILE  \t\t the output file\n\
-SPLIT_FILE   \t\t when calculating cross entropy, a config file specifying types to consider\n\
---------------------------------------------------------------\n\
-BACKOFF      \t\t use the back-off technique\n\
-CACHE        \t\t use the cache technique \n\
              \t\t (types: WINDOW_CACHE, SCOPE_CACHE)\n\
              \t\t (default is cache window of 1000 words)\n\
-CACHE_ONLY   \t\t only use the cache technique without ngrams\n\
-CACHE_ORDER  \t\t the maximum order of ngrams used in the cache (default: 3)\n\
-CACHE_DYNAMIC_LAMBDA \t dynamic interpolation weight for -cache (H/(H+1)), default option\n\
-CACHE_LAMBDA \t\t interpolation weight for -CACHE\n\
-WINDOW_CACHE \t\t build the cache on a window of n tokens (default n=1000)\n\
-WINDOW_SIZE  \t\t the size of cache, default: 1000 tokens\n\
-FILE_CACHE  \t\t build the cache on a file or related files\n\
-SCOPE_FILE   \t\t the scope file for scope cache on CLASS or METHOD\n\
-RELATED_FILE \t\t when using cache on file scope, build the cache on the related files\n\
              \t\t FILE_DIR should be given\n\
-FILE_DIR     \t\t the directory that stores all files\n\
---------------------------------------------------------------\n\
";


int main(int argc, const char* argv[])
{
    srand(time(0));
    getRandom(); // I'm sticking one in here b/c the first pseudo random num seems to be rather consistent.
    //I see greater variance calling it once before hand.
    cout << copy_right << endl;
    
    if (argc < 9)
    {
        cerr << "read parameters err, please check your parameter list" << endl;
        cout << help_info << endl;
        return 1;
    }

    if (!Data::ReadConfig(argc, argv))
    {
        cout << help_info << endl;
        return 1;
    }

    Suggestion suggestion;
    if(!Data::GENERATE) //Create new data option to select --GENERATE MODE.
    {
      suggestion.Process();
    }
    else
    {
      cout << "Generating Tokens" << endl;
      //Or should I read them in Generate??
      suggestion.Generate();
    }
        
	return 0;
}

