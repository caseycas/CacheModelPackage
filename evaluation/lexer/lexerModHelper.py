"""
Helper file for lexer modifications to the text as
decided by flags.
"""
from utilities import *
from fileUtilities import *
from dictUtils import *
from pygments.lexers import get_lexer_for_filename
from pygments import lex


def preprocessFile(path, basePath):
    """
    Perform preprocessing on the lexer.
    Parameters:
    -----------
    path
    basePath
    Returns:
    -----------
    (curProject - The current project or corpora we are in
     curFile - The corresponding original file path
     lexedWoComments - the Pygments token list with preprocessing
     OR (Not yet implemented) Something for English?,
     language - the language of this lexer
     fileErrorCount - count of observed error tokens from Pygments)
    """
    if(True): #TODO is a programming language.
        components = path.split(".")
        fileContents = ""
        fileContents = ''.join(open(path, 'r').readlines())

        lexer = get_lexer_for_filename(path)
        tokens = lex(fileContents, lexer) # returns a generator of tuples
        tokensList = list(tokens)
        language = languageForLexer(lexer)
        (curProject, curFile) = getProjectAndFilename(path, basePath)

        # Strip comments and alter strings
        lexedWoComments = tokensExceptTokenType(tokensList, Token.Comment)
        lexedWoComments = tokensExceptTokenType(lexedWoComments, 
                                                Token.Literal.String.Doc)
        beforeError = len(lexedWoComments)
        #Remove Things than didn't lex properly
        lexedWoComments = tokensExceptTokenType(lexedWoComments, Token.Error)
        fileErrorCount = beforeError - len(lexedWoComments)

        #Alter the pygments lexer types to be more comparable between our 
        #languages
        lexedWoComments = fixTypes(lexedWoComments, language) 
        lexedWoComments = convertNamespaceTokens(lexedWoComments, language)

    return(curProject, curFile, lexedWoComments, language, fileErrorCount)

def collapseLiterals(litFlag, lexedWoComments):
    """
    Handle literals as specified by litFlag.

    Parameters:
    litFlag - [0,1,2,3,4]
        0 -> replace all spaces in strings with _
        1 -> replace all strings with a <str> tag.
        2 -> add spaces to the ends of the strings
        3 -> collapse strings to <str> and collapses numbers to a type as well.
        4 -> collapses strings and numbers to a few common types e.g empty, 0, 
             1, -1, and the rest to generic types.

    lexedWoComments - A Pygments tokenlist (list of tuples)

    Returns:
    --------
    A new pygments tokenlist with the literals modified as described.
    """
    if(litFlag == 0):
        lexedWoComments = modifyStrings(lexedWoComments, underscoreString)
    elif(litFlag == 1):
        lexedWoComments = modifyStrings(lexedWoComments, singleStringToken)
    elif(litFlag == 2):
        lexedWoComments = modifyStrings(lexedWoComments, spaceString)
    elif(litFlag == 3):
        lexedWoComments = modifyStrings(lexedWoComments, singleStringToken)
        lexedWoComments = collapseStrings(lexedWoComments)
        lexedWoComments = modifyNumbers(lexedWoComments, singleNumberToken)
    elif(litFlag == 4):
        lexedWoComments = modifyStrings(lexedWoComments, threeTypeToken)
        lexedWoComments = collapseStrings(lexedWoComments) #Do I need this?
        lexedWoComments = modifyNumbers(lexedWoComments, keepSmallNumToken)
    else:
        print("Not a valid string handling flag. Valid types are currently 0, 1, 2, 3, and 4")
        quit()

    return(lexedWoComments)

def updateVocab(vocab, tokens):
    """
    Update the vocabulary based on the tokens of this file.

    Parameters:
    -----------
    vocab - a dictionary of word, count

    tokens - a pygments tokenlist of tuples

    Returns:
    ---------
    vocab -> the dictionary in the parameters with counts 
    updated.
    """
    for token_type, token in tokens:
        if(token.strip() != ""):
            vocab = addToDictCount(vocab, token.strip())

    return vocab


def cutoffCounts(vocab):
    """
    Given a vocab, return a dict matching
    the number of words occuring more than X times
    where X is each of the keys.

    Parameters:
    ----------
    vocab - a dictionary of word -> count

    Returns:
    --------
    A ordered dictionary of Count -> Words that appear more than Count
    Ordered such that we have words that occur more than 1 time, 2 times,
    etc (Skipping any case where we have nothing at that point.)
    """
    countOfCounts = OrderedDict()
    #Order the dictionary as a list of tuples (ascending order)
    vocab_count_list = sorted([count for word, count in vocab.items()])
    for item in vocab_count_list:
        #Increment all keys in countOfCounts by 1.
        for key in countOfCounts.keys():
            countOfCounts = addToDictCount(countOfCounts, key)

        #If bigger than seen before, add a slot for this key as well.
        if(item not in countOfCounts.keys()):
            countOfCounts[item] = 1

    return(countOfCounts)

def vocabCutoff(fullVocab, sizeCap):
    """
    Return a vocabulary that is less than sizeCap. 
    Pick from the dictionary a frequency cutoff such that the 
    number of tokens occurs at least that number of times <= sizeCap
    If len(fullVocab < sizeCap) return all words in the vocab.
    Parameters:
    -----------
    fullVocab - a dictionary of all words and their counts

    sizeCap - an integer for the maximum allowable vocabulary size.

    Returns:
    --------
    truncVocab - a set of tokens <= sizeCap
    based on the frequencies recorded in fullVocab.

    """
    if(len(fullVocab) <= sizeCap):
        return(set(fullVocab.keys()))

    countOfCounts = cutoffCounts(fullVocab)
    #print(fullVocab)
    #print(countOfCounts)
    expectedSize = 0
    cutoff = 1
    #Find at which count we are below the necessary vocab size.
    for occuranceCount, vocabSize in countOfCounts.iteritems():
        if(vocabSize < sizeCap):
            expectedSize = vocabSize
            cutoff = occuranceCount
            break
    
    newVocab = set()

    for word, count in fullVocab.iteritems():
        if(count >= cutoff):
            newVocab.add(word)

    assert(len(newVocab) == expectedSize)

    return(newVocab)