#!/usr/bin/env python

import os
import os.path
import sys


def cross(input_file_dir, fold_num, options, order, split_file = ""):
    pipes = [os.pipe() for i in xrange(fold_num)]
    
    for i in xrange(fold_num):
        pid = os.fork()
        if pid == 0:
            os.close(pipes[i][0])
 
            train_file = '%s/fold%d.train' % (input_file_dir, i)
            test_file = '%s/fold%d.test' % (input_file_dir, i)
            scope_file = '%s/fold%d.scope' % (input_file_dir, i)
            if(split_file == ""):
                print './completion %s -NGRAM_FILE %s.%dgrams -NGRAM_ORDER %d -SCOPE_FILE %s -INPUT_FILE %s -OUTPUT_FILE %s.output | tee %s.log' % (options, train_file, order, order, scope_file, test_file, test_file, test_file)
                os.system('./completion %s -NGRAM_FILE %s.%dgrams -NGRAM_ORDER %d -SCOPE_FILE %s -INPUT_FILE %s -OUTPUT_FILE %s.output | tee %s.log' % (options, train_file, order, order, scope_file, test_file, test_file, test_file))
            else:
                print './completion %s -NGRAM_FILE %s.%dgrams -NGRAM_ORDER %d -SCOPE_FILE %s -INPUT_FILE %s -OUTPUT_FILE %s.output -SPLIT_FILE %s | tee %s.log' % (options, train_file, order, order, scope_file, test_file, test_file, split_file, test_file)
                os.system('./completion %s -NGRAM_FILE %s.%dgrams -NGRAM_ORDER %d -SCOPE_FILE %s -INPUT_FILE %s -OUTPUT_FILE %s.output -SPLIT_FILE %s | tee %s.log' % (options, train_file, order, order, scope_file, test_file, test_file, split_file, test_file))
            sys.exit()
        else:
            os.close(pipes[i][1])
    
    for p in pipes:
        os.wait()
    

if __name__ == '__main__':
    input_file_dir = sys.argv[1]
    order = int(sys.argv[2])
    fold_num = 10
    if(sys.argv[3] == "-SPLIT_FILE"):
        options = ' '.join(sys.argv[5:])
        split_file = sys.argv[4]
        if(os.path.isfile(split_file)):
            cross(input_file_dir, fold_num, options, order, split_file)
        else:
            print(split_file + ", your file of types to consider, does not exist.")
            quit()
    else:
        options = ' '.join(sys.argv[3:])
        cross(input_file_dir, fold_num, options, order)
