# Version .2
# CacheModelPackage
This is a package that contains a modified version of Zhaopeng's Cache model
(see http://dl.acm.org/citation.cfm?id=2635875).  I've modified the scripts
for robustness and ease of use.  While the original Cache model was based
on SRILM language models, this allows for the swapping out to the model of your
choice.

#OS and Dependency Requirements
Along with the language models, this package uses a combination of C++ and python 2.7.
If you want to make use of the lexer (required for the generative mode), you must also
have the Pygments library installed, e.g. run:

    pip install Pygments

I have currently tested this package on Ubuntu and MacOSX.  Further tests with OSX and
maybe windows will be provided in the future.

# Installing Language Models

This package is set up to be able to swap out different language models and train and test with them.  The cache model is then built on top of them. For convenience, I've provided binaries for SRILM and MITLM that have worked for me on linux (Ubuntu 15.10) and Mac OS X (10.11), under evaluation/srilm or evaluation/mitlm.  If these binaries do not work for you, I've 
included some instructions to compile them from source.  Currently, it seems the SRILM binary is portable to other systems,
but MITLM must be compiled from source on your own machine.

#Mitlm
On Linux:
    git clone https://github.com/mitlm/mitlm.git ~/mitlm
    sudo apt-get install gfortran autoconf automake libtool autoconf_archive
    cd ~/mitlm
    ./autogen.sh
    ./configure
    make
    make install
On Mac (source: https://github.com/eddieantonio/mitlm/issues/49):
To install from brew as a command line tool (this is where the included estimate ngram comes from):

    brew tap eddieantonio/eddieantonio
    brew install mitlm

Then you can run "estimate-ngram ...."
To install from source via brew, you can try:

    brew install libtool autoconf gcc
    ./autogen.sh --prefix=/usr/local
    make
    make install

I have not successfully compiled from source on MAC OSX, but there is a variety of advice on doing so in these issues:
https://github.com/jrwdunham/old/issues/32
https://github.com/mitlm/mitlm/issues/42
http://simon-joseph.github.io/mitml-osx-yosemite/


#Srilm
I've included binaries for the relevant SRILM programs in ./evaluation/.  They should work on linux or mac machines. 
If these do not work, you need to compile from source.  This requires a license from www.speech.sri.com/projects/srilm
Follow the steps in the included INSTALL file to compile from source.  Additional MacOSX instructions can be found here:
http://www1.icsi.berkeley.edu/~wooters/SRILM/

#KenLM
Instructions incoming.

#Sample corpora
There are several sample corpora provided in the package. 

The java corpus is a random sample of files from 12 java projects (apache/cassandra, gradle/gradle,
clojure/clojure, junit-team/junit, deeplearning4j/nd4j, libgdx/libgdx, 
netty/netty, eclipse/ide, nostra13/Android-Universal-Image-Loader, 
elastic/elasticsearch, ReactiveX/RxJava, google/guava) all from github except
the eclipse ide.  

The full version of the corpus (minus very large source code files) can be found at
full_java. This is almost 17 million tokens in size.  Due to size difference, entropy
values may not be comparable to smaller corpora.

The ruby corpus is a random sample of ruby files from 15
projects (cloudfoundry/bosh, Homebrew/homebrew, rapid7/metasploit-framework, 
diaspora/diaspora, jekyll/jekyll, rubinius/rubinius, discourse/discourse, 
mysociety/alaveteli, ruby/ruby, fog/fog, puppetlabs/puppet, sass/sass, 
gitlabhq/gitlabhq, rails/rails, zunda/emoticommits).  

The english corpus is simply the Brown Corpus obtained from nltk.  The random samples 
of the code corpora were choosen to bring their size down to about 1 million tokens, 
the same as the Brown corpus. 

As a final note, the current ruby and java corpora have been lexed in such a 
way to collpase string and number literals to a few types (like &lt;str&gt;, &lt;int&gt;, 
etc).

Additionally, I've included a variety of domain specific variants of english listed below: 

The Shakespeare corpus was obtained from http://norvig.com/ngrams/ and split into separate files, and
is slightly under 1 million tokens.

The Scifi corpus is take from a selection of 20 scifi books from the Gutenberg corpus. It is approximately
1.5 million tokens.  See https://www.gutenberg.org/wiki/Science_Fiction_(Bookshelf) for details.

The legal corpus is a lexed version of the US Code, minus Title 41.  It is slightly over 2 million tokens.
See http://uscode.house.gov/download/download.shtml for details.

The NASA corpus was obtained by html scraping of active NASA directives.  It is approximately a quarter of
a million tokens.  See http://nodis3.gsfc.nasa.gov/Rpt_current_directives.cfm for the list of these
directories.

# Changing language model (How to modify lm.ini)

The file evaluation/scripts/lm.ini contains information that must be set to choose what language model is used.
I've include commented out suggestions for how to select your language model, which requires two* items.
The first is the variable model_type, which selects which language model to run.  Currently, this is either
SRILM or MITLM.  The second is location, which is the path to the binary for this language model.  Using mitlm
as an example, which uses the 'estimate-ngram' binary:

    model_type = MITLM
    location = ~/mitlm/bin/estimate-ngram

*SRILM requires two binaries to run 'ngram-count' and 'ngram'.  These must be specified as in variables as
location and location2 respectively. So, for example, srilm could be configured as your model like this:

    model_Type = SRILM
    location = ~/srilm/bin/ngram-count
    location = ~/srilm/bin/ngram


#Compiling Cache Model Code
The directory evaluation/cachemodel contains the source for producing the entropies
from the language model files.  Before running, you must run:

    cd evaluation/cachemodel
    make
    cp completion ../

#Running Instructions
I've provided sample shell scripts in evaluation to create cache and no cache models.  These are located in evaluation/.  To run the java one from example, 
type "sh java_example.sh".  I will use this shell script to explain the folder
structure.

    mkdir -p ./results/entropy/java/summary

First, create some directories to store the output. The evalation/results/java directory will store the raw entropy output from the code with additional debug
information.  The summary directory below this will store a csv file that 
summarizes the entropies for each test set.

    ./scripts/train.py ./data/java/ 3 1.0 2

The train.py script is a wrapper to run a 10-fold cross validation on a corpus 
with a selected language model.  These are specified in evaluation/scripts/lm.ini.
In the .ini file, we specifiy model_type, which tells what language model to use
and location (location2 for srilm), which tells train.py where your language model
binary is stored.  The arguments train.py takes are the location of your corpus
(see Zhaopeng's README "old_readme.txt" for the directory structure here),
the order of ngrams, a float between 0.0 and 1.0 to test and train only on a random
fraction of the data, and an option for splitting.  Running "train.py -h" can 
provide additional information.  If you are just testing this out, just use 1.0 
and 2 as the final arguments.

    ./scripts/cross.py ./data/java/ 3 -ENTROPY -BACKOFF -DEBUG -CACHE -CACHE_ORDER 3 -CACHE_DYNAMIC_LAMBDA -WINDOW_CACHE -WINDOW_SIZE 5000 -FILES > ./results/entropy/java/3gramsCache.txt
    ./scripts/cross.py ./data/java/ 3 -ENTROPY -BACKOFF -DEBUG -FILES > ./results/entropy/java/3gramsNoCache.txt

These 2 commands run the 10 test sets against the 10 trained models created by 
train.py. The flags are forwarded to the completion binary, whose arguments are
detailed in "old_readme.txt"  Here, the first command is creating a trigram model
with trigram 5000 token window cache and dynamic lambda.  The -DEBUG option
produces additional output in ./data/java where the individual entropies for each
token are display.  Replacing with -TEST is faster, but this information is lost.

(Optional: What does all the output in the evaluation/data/java mean?)
If you look at evaluation/data/java after running train.py and cross.py, you'll 
see several new files.  I will provide a brief explanation of the relevant ones 
here.  Each is referenced by a fold0, fold1, etc, which refers to what fold it is 
in.  Using fold0 as an example:

* fold0.test - A list of the files to be used in this fold's test set.
* fold0.train - This is a merged set of tokens, one file per line of this fold's training data.
* fold0.test.log - The individual outputs of ./completion, which are combined in
* evaluation/results/entropy/java/*.txt
* fold0.test.output - The per token entropy data, output by using the -DEBUG option.
* fold0.train.3grams - The ARPA format language models built from this training 
split.


    python ./scripts/convertCacheResults.py ./results/entropy/java/ ./results/entropy/java/summary/3grams.csv

This final step is a convenience script to convert the output of the models into a
csv file. Each ngram order and cache/no cache option gets its own column in the 
csv. From our java sample, we have columns "java3Cache3" and "java3NoCache" which
respectively mean a java trigram cache model that also has a trigram cache, and a
java trigram model with no cache.

#Generation Mode

If you wish to see what suggestions the language model will generate for some code or text,
there is a -GENERATE mode for the completion tool.  I have added a python script generate.py in
evaluation/scripts to make this easier to manage.  Running python ./scripts/generate.py -h
wil provide some additional information about the arguments, but for example if you typed:

    python ./scripts/generate.py "import java.io" data/java/fold0.train.3grams 3 2 java

The script will use "import java.io" as the base on which to generate, data/java/fold0.train.3grams is the .arpa
language model file it will use to generate new tokens, 3 tells the script that you are using a trigram model,
2 is the number of new tokens to generate after the base, and java is the language (used for lexing the string).

Note: The Generation Mode currently just uses the raw ngram language model and does not make use of the cache.

# Find a Bug?

If you find any bugs or run into problems while running this package, please open an issue and let me know. 