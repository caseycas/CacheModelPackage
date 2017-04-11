import nltk
import sys
import re
import os

punct = [",", ".", "\"", ",\"","'",";", ".\"", "-", "?", "--", ":", "!\"", "?\"", "!", "?--", ".--", "!--", "\'" ,"\'\'", "``", "`", "(", ")", "/", "&","<QUOTE>", "<", ">"]


#Is the line all capital letter except for punctuation.
def isTitle(line):
    return re.search("^[ A-Z\W]+$",line.strip()) != None


def getPOSUnderscore(word):
    '''
    Alter sentences in the style word_POS to just be the POS
    '''
    pos_s = word.split("_")
    if(len(pos_s) > 1):
        return word.split("_")[-1]
    else:
        if(pos_s[0] not in punct):
            print(pos_s)
            return "UNK"
        else:
            return pos_s[0]


def removePunct(text):
    newText = []
    for t in text:
        tmp = t
        if(tmp not in punct):
            for p in punct:
                tmp = tmp.replace(p, "")
            
            newText.append(tmp)

    return newText


#Let's just drop the contraction part of it?
def filterStopwords(toRemove, text):
    '''
    Use stopwords2.txt if you want to remove split contractions (such as in the big english corpus, brown doesn't have this problem.)
    '''
    temp = []
    for t in filter(lambda t: t.lower() not in toRemove, text):
        tmp = t
        if(tmp not in toRemove):
            for p in punct:
                tmp = tmp.replace(p, "")
            temp.append(tmp)

    return temp
