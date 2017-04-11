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

def train(data_dir, train, valid, order):
    """
    Merge and the training and validation file as one set
    and train an ngram model of size "order" based on the
    parameters in lm.ini
    Parameters:
    -----------
    train - the training file
    valid - the validation file
    order - the ngram order
    Returns:
    --------
    """
    discountStr = buildSmoother(order)

    #Merge train and valid (if not merged already)
    merged_file = os.path.join(data_dir, "train_valid")
    if(os.path.isfile(merged_file) == False):
        with open(merged_file, 'w') as f:
            with open(os.path.join(data_dir, train), 'r') as in_t:
                words = in_t.read()
                f.write(words)
            with open(os.path.join(data_dir, valid), 'r') as in_v:
                words = in_v.read()
                f.write(words)

    modelSelect(merged_file, order)



#Inputs: test, valid, train, lm train file.
parser = argparse.ArgumentParser(description="This script is intented to use "+
                                  "Zhaopeng's cache model in a way that is "+
                                  "comparable to the values used in the lstm"+
                                  "model. This means that we have a fixed"+
                                  "train and testing set, rather than picking"+
                                  " them as random 10-fold breaks.") 
parser.add_argument("data_dir", help = "The input data directory.", action=
                    "store", type=str)

parser.add_argument("train_file",help = "The training file.", action="store", 
                    type=str)
parser.add_argument("valid_file",help = "The validation file.", action="store", 
                    type=str)
#parser.add_argument("test_file",help = "The testing file.", action="store", 
#                    type=str)
parser.add_argument("ngram_order", help = "The order of ngrams to use.",
                    action="store", type=int)
#parser.add_argument("lm_file",help= "The .ini file for training", 
#                   action="store", type=str)

args = parser.parse_args()

train(args.data_dir, args.train_file, args.valid_file, args.ngram_order)
