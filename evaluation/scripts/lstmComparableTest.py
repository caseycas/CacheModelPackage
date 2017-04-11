import argparse
import os
from utils import *

"""
LSTM comparable training.
This script is intented to use Zhaopeng's cache model in a way
that is comparable to the values used in the lstm model.
This means that we have a fixed train and testing set, rather
than picking them as random 10-fold breaks.

"""


parser = argparse.ArgumentParser(description="This script is intented to use "+
                                  "Zhaopeng's cache model in a way that is "+
                                  "comparable to the values used in the lstm"+
                                  "model. This means that we have a fixed"+
                                  "train and testing set, rather than picking"+
                                  " them as random 10-fold breaks.") 

parser.add_argument("data_dir", help = "Path to where the train, valid and " +
                    " test files are stored.", action="store",type=str)
parser.add_argument("train_file",help = "The training file name.", action="store", 
                    type=str)

parser.add_argument("test_file",help = "The testing file.", action="store", 
                    type=str)
parser.add_argument("ngram_order", help = "The order of the ngrams to test.",
                    action="store", type=int)

parser.add_argument("completion_args", help = "The rest of the arguments to " +
                    "Zhaopeng's completion binary.", nargs="*")

args = parser.parse_args()

options = " ".join(args.completion_args)
runTest(args.data_dir, args.train_file, args.test_file, args.ngram_order, options)

