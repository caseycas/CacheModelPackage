#ifndef __NGRAM_H__
#define __NGRAM_H__
#include <string>
#include <iostream>
#include <fstream>
#include <vector>
#include <ctime>

#include <math.h>

#include "utility.h"

using namespace std;

class Word
{
public:
    Word()
    {
        m_prob = 0.0;
    }

    Word(const string& token, const float prob)
    {
        m_token = token;
        m_prob = prob;
    }

    bool operator <(const Word &right) const
    {
        return m_prob < right.m_prob;
    }

    bool operator >(const Word &right) const
    {
        return m_prob > right.m_prob;
    }

    string m_token;
    float m_prob;
    string m_debug;
};

class Ngram
{
public:
    // for prediction task
	Ngram(const string& ngramFile, const int order, const int beam_size);
    // for calculating the cross entropy
	Ngram(const string& ngramFile, const int order);
public:	
    // for prediction task
    /**
    * get the candidate tokens when given the prefix
    * @param prefix the previous (n-1) grams
    * @param use_backoff Using back-off, when there is no candidates given (n-1) grams,
                        we will search the candidates given the previous (n-2) grams,
                        ...
                        until candidates are returned
    * @param candidates the result candidates
    **/
	bool GetCandidates(const std::string& prefix, const bool use_backoff, vector<Word>& candidates);
    
    // for calculating the cross entropy
    /**
    * get the candidate tokens when given the prefix
    * @param prefix the previous (n-1) grams
    * @param use_backoff Using back-off, when there is no candidates given (n-1) grams,
                        we will search the candidates given the previous (n-2) grams,
                        ...
                        until candidates are returned
    * @param candidates the result candidates
    **/
    float GetProbability(const string& prefix, const string& token, const bool use_backoff);

    float m_unk_prob;
private:
    // for prediction task
    // the vector that stores the candidates word given all n-grams (i.e., 1-grams, 2-grams, ..., (n-1)-grams)
    vector<map<string, vector<Word> > > m_ngrams_list;

    // for calculating the cross entropy
    // the map that stores the candidates word given all n-grams (i.e., 1-grams, 2-grams, ..., (n-1)-grams)
    vector<map<string, map<string, float> > > m_ngrams_map;
};
#endif

