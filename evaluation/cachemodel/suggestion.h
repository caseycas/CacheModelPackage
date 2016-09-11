#ifndef __SUGGESTION_H__
#define __SUGGESTION_H__
#include <string>
#include <iostream>
#include <fstream>
#include <vector>
#include <set>
#include <ctime>

#include "utility.h"
#include "data.h"

using namespace std;

class Suggestion
{
public:
    void Process();
    void Generate();
private:
    void DealFiles();

    void DealFile(const string& input_file);

    // for code prediction
    // {
    void Predict(const vector<string>& tokens);
    /**
    * get the candidate words when given the previous words
    * @param prefix the previous (n-1) grams
    * @param candidates the result candidates
    **/
	void GetCandidates(const string& prefix, const string& cache_prefix, vector<Word>& candidates);
    // }
 
    // for calculating the cross entropy
    // {
    float GetProbability(const string& prefix, const string& cache_prefix, const string& token, string& debug_info);
    // }
   
    int m_total_number;
    // for calculating accuracy of prediction
    float m_mrr;    // mean reciprocal rank (1/n \sum (1/rank))
    int m_top1_correct;
    int m_top5_correct;
    int m_top10_correct;
    // for cross entropy
    float m_total_prob;
    int m_total_type_number; // A running sum of considered tokens of a specific type. (Used when SPLIT_FILE provided)
    vector<string> consideredTypes; //If SPLIT_FILE is enabled, contains a list of types to average entropy over.
    bool invertTypes;
    
    // measurement for each file
    int m_file_total_number;
    // for calculating accuracy of prediction
    float m_file_mrr;    // mean reciprocal rank (1/n \sum (1/rank))
    int m_file_top1_correct;
    int m_file_top5_correct;
    int m_file_top10_correct;
    // for cross entropy
    float m_file_prob;

    // common usage
    ofstream m_fout;
    set<int> m_class_scope_begins,
             m_class_scope_ends,
             m_method_scope_begins,
             m_method_scope_ends;
    vector<string> m_related_files;

    // return: rank position for in, 0 for not in
    int GetRank(const vector<Word>& candidates, const string& ref);
    // return: 1 for in, 0 for not in
    int Is_in(const vector<Word>& candidates, const string& ref, const int top_n);

    void ReadScope(const string& scope_file_name);

    // return: one of the candidates based on the probabilities.
    // assumes suggestions are in rank order...
    Word selectCandidate(const vector<Word>& candidates, const vector<float>& probs);
};
#endif

