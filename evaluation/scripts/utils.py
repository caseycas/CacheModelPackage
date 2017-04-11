from Config import Config
import os
LMFILE = os.path.dirname(os.path.realpath(__file__)) + "/lm.ini"

def buildSmoother(order):
    output = ""
    for i in range(1, order+1):
        output += "-kndiscount" + str(i) + " "
        #output += "-wbdiscount" + str(i) + " "
        #output += "-cdiscount" + str(i) + " .5 "
    return output

def modelSelect(train_file, order):
    #File path to lm.ini depends on where you run it

    config_file = Config(LMFILE)
    lm_args = config_file.ConfigSectionMap("language_model")
    if(lm_args["model_type"] == "MITLM"):
        #Get vocab...
        print("%s -t %s -write-vocab %s.vocab" % (lm_args["location"],train_file, train_file))
        os.system("%s -t %s -write-vocab %s.vocab" % (lm_args["location"],train_file, train_file))
        #Alternative uses mitlm instead...
        print('%s -order %d -v %s.vocab -unk -smoothing ModKN -t %s -write-lm %s.%dgrams' % (lm_args["location"],order, train_file, train_file, train_file, order))
        os.system('%s -order %d -v %s.vocab -unk -smoothing ModKN -t %s -write-lm %s.%dgrams' % (lm_args["location"],order, train_file, train_file, train_file, order))
    elif(lm_args["model_type"] == "SRILM"):
        #Original Srilm
        print('%s -text %s -lm %s.kn.lm.gz -order %d -unk -kndiscount -interpolate' % (lm_args["location"],train_file, train_file, order))
        os.system('%s -text %s -lm %s.kn.lm.gz -order %d -unk -kndiscount -interpolate' % (lm_args["location"],train_file, train_file, order))
        print('%s -lm %s.kn.lm.gz -unk -order %d -write-lm %s.%dgrams' % (lm_args["location2"],train_file, order, train_file, order))
        os.system('%s -lm %s.kn.lm.gz -unk -order %d -write-lm %s.%dgrams' % (lm_args["location2"],train_file, order, train_file, order))
        os.system('rm %s.kn.lm.gz' % train_file)
    elif(lm_args["model_type"] == "KENLM"):
        #Kenlm
        print('%s -o %d --interpolate_unigrams 0 <% >%s.%dgrams'% (lm_args["location"],order, train_file, order))
        os.system('%s -o %d --interpolate_unigrams 0 <%s >%s.%dgrams'% (lm_args["location"],order, train_file, train_file, order))
    else:
        print("This is not a recognized language model.")
        print("Check ./lm.ini to make sure \'model\' is one")
        print("of MITLM,SRILM,or KENLM")

def runTest(input_file_dir, train_file, test_file, order, options):
    scope_file = "placeholder.scope"
    train_file = os.path.join(input_file_dir, train_file)
    test_file = os.path.join(input_file_dir, test_file)
    os.system('touch %s' % (os.path.join(input_file_dir, scope_file)))
    test_link = os.path.join(input_file_dir, "test_link")
    with open(test_link, 'w') as f:
        f.write(test_file)

    print './completion %s -NGRAM_FILE %s.%dgrams -NGRAM_ORDER %d -SCOPE_FILE %s -INPUT_FILE %s -OUTPUT_FILE %s.output | tee %s.log' % (options, train_file, order, order, scope_file, test_link, test_file, test_file)
    os.system('./completion %s -NGRAM_FILE %s.%dgrams -NGRAM_ORDER %d -SCOPE_FILE %s -INPUT_FILE %s -OUTPUT_FILE %s.output | tee %s.log' % (options, train_file, order, order, scope_file, test_link, test_file, test_file))
