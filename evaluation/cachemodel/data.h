#ifndef __DATA_H__
#define __DATA_H__

#include <string>
#include <string.h>
#include <iostream>
#include <vector>
#include <map>
#include <sstream>

#include "ngram.h"
#include "cache.h"

using namespace std;

class Data
{
public:
    //read config parameters
    static bool ReadConfig(const int &argc, const char* argv[]);
	
    static string INPUT_FILE;
    static string NGRAM_FILE;
    static string OUTPUT_FILE;
    static int NGRAM_ORDER;
     
    static bool TEST;
    static bool FILES;

    static bool ENTROPY;
    
    /**
    Using back-off, when there is no candidates given (n-1) grams,
    we will search the candidates given the previous (n-2) grams,
    ...
    until candidates are returned or no prefix could be given
    **/
    static bool USE_BACKOFF;

    static bool USE_CACHE;
    static int CACHE_ORDER;
    static bool USE_WINDOW_CACHE;
    static int WINDOW_SIZE;
    static bool USE_FILE_CACHE;
    static string SCOPE_FILE;
    static bool USE_RELATED_FILE;
    static string FILE_DIR;
    static float CACHE_LAMBDA;
    static bool CACHE_DYNAMIC_LAMBDA;
    
    static bool USE_CACHE_ONLY;
    
    static int BEAM_SIZE;

    static bool DEBUG;

    static string SPLIT_FILE; //A config file to show what entropy type tokens to take
    
    static Ngram* NGRAM;
    static Cache CACHE;


private:
    static bool Check();
    static void Show();
};
#endif

