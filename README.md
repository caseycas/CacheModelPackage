# Version .1
# CacheModelPackage
This is a package that contains a modified version of Zhaopeng's Cache model
(see http://dl.acm.org/citation.cfm?id=2635875).  I've modified the scripts
for robustness and ease of use.  While the original Cache model was based
on SRILM language models, this allows for the swapping out to the model of your
choice.

I have currently tested this package on Ubuntu.  Further tests with OSX and
maybe windows incoming.

# Installing Language Models

This package is set up to be able to swap out different language models and train and test with them.  The cache model is then built on top of them. While the projects themselves include additional instructions for installation, I'm including the commands I need to use to get them working on Ubuntu 15.10

#Mitlm
git clone https://github.com/mitlm/mitlm.git ~/mitlm
sudo apt-get install gfortran autoconf automake libtool autoconf_archive
cd ~/mitlm
./autogen.sh
./configure
make
make install

#Srilm
I've included binaries for the relevant SRILM programs in ./evaluation/scripts.  They should work on linux machines. If these do not work, you need to compile
from source.  This requires a license from www.speech.sri.com/projects/srilm

#KenLM
Instructions incoming.

#Sample corpora
There are several sample corpora provided in the package.  The java corpus is a 
random sample of files from 12 java projects (apache/cassandra, gradle/gradle,
clojure/clojure, junit-team/junit, deeplearning4j/nd4j, libgdx/libgdx, 
netty/netty, eclipse/ide, nostra13/Android-Universal-Image-Loader, 
elastic/elasticsearch, ReactiveX/RxJava, google/guava) all from github except
the eclipse ide.  The ruby corpus is a random sample of ruby files from 15
projects (cloudfoundry/bosh, Homebrew/homebrew, rapid7/metasploit-framework, 
diaspora/diaspora, jekyll/jekyll, rubinius/rubinius, discourse/discourse,  
mysociety/alaveteli, ruby/ruby, fog/fog, puppetlabs/puppet, sass/sass, 
gitlabhq/gitlabhq, rails/rails, zunda/emoticommits).  The english corpus is 
simply the Brown Corpus.  The random samples of the code corpora were choosen
to bring their size down to about 1 million tokens, the same as the Brown corpus.
As a final note, the current ruby and java corpora have been lexed in such a 
way to collpase string and number literals to a few types (like <str>, <int>, 
etc).


#Compiling Cache Model Code
The directory evaluation/cachemodel contains the source for producing the entropies
from the language model files.  Before running, you should run:

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
fold0.test - A list of the files to be used in this fold's test set.
fold0.train - This is a merged set of tokens, one file per line of this fold's training data.
fold0.test.log - The individual outputs of ./completion, which are combined in
evaluation/results/entropy/java/*.txt
fold0.test.output - The per token entropy data, output by using the -DEBUG option.
fold0.train.3grams - The ARPA format language models built from this training 
split.


python ./scripts/convertCacheResults.py ./results/entropy/java/ ./results/entropy/java/summary/3grams.csv

This final step is a convenience script to convert the output of the models into a
csv file. Each ngram order and cache/no cache option gets its own column in the 
csv. From our java sample, we have columns "java3Cache3" and "java3NoCache" which
respectively mean a java trigram cache model that also has a trigram cache, and a
java trigram model with no cache.