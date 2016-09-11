#include "suggestion.h"

void Suggestion::Generate()
{
    vector<Word> candidates; //These are Words, not strings, what's the difference? Why do I need this?
    vector<Word> output;
    vector<string> context;
    string prefix = "";
    context.push_back("<s>");
    int genCount = Data::GENCOUNT;
    string debug_info;


    ifstream fin(Data::INPUT_FILE.c_str());
    string line, token;
    while (getline(fin, line))
    {
        stringstream ss(line);

        while (ss >> token)
        {
            context.push_back(token);
        }
    }

    cout << "Input file read" << endl;
    int end = context.size() + genCount;
    //Word has the probs built into them.
    for(int c_tok = context.size(); c_tok < end; c_tok++)
    {
        int start = c_tok-(Data::NGRAM_ORDER-1)>0? c_tok-(Data::NGRAM_ORDER-1) : 0;
        cout << c_tok << "/" << end << endl;
        cout << "Start: " << start << endl;
        Join(context, start, c_tok-1, prefix);
        cout << "Prefix: " << prefix << endl;
        Suggestion::GetCandidates(prefix, prefix, candidates);

        cout << candidates.size() << " Candidates selected for spot " << c_tok << endl;
        cout << "Prefix is " << prefix << endl;
        for(int i = 0; i < candidates.size(); i++)
        {
            cout << "Candidate " << i << ": " << candidates[i].m_token << endl;
        }

        //Iterate over the words suggested.
        vector<float> probs(candidates.size());
        /*
        for(int i = 0; i < probs.size(); i++)
        {
            probs[i] = Suggestion::GetProbability(prefix, prefix, candidates[i], debug_info);
        }*/
        for(int i = 0; i < probs.size(); i++)
        {
            probs[i] = candidates[i].m_prob;
        }
        //TODO: Normalize the probabilities and pick one?
        float sum = 0;
        for(int i = 0; i < probs.size(); i++)
        {
            sum += probs[i];
        }
        for(int i = 0; i < probs.size(); i++)
        {
            probs[i] = probs[i]/sum;
        }
        //TODO: Is candidates ordered in terms of probabilities?
        for(int i = 0; i < probs.size(); i++)
        {
            cout << "Candidate: " << candidates[i].m_token << " Original Prob: " << candidates[i].m_prob << " Prob: " << probs[i] << endl;
        }
        Word candidate = Suggestion::selectCandidate(candidates, probs);
        //Update the context
        context.push_back(candidate.m_token);
        output.push_back(candidate);
    }

    cout << "Context: " << endl;

    for(int i = 0; i < context.size(); i++)
    {
        cout << context[i] << " ";
    }

    cout << endl << "Generated Tokens: " << endl;

    for(int i = 0; i < output.size(); i++)
    {
        cout << output[i].m_token << " ";
    }
    cout << endl;
}

void Suggestion::Process()
{
    // initilize the statistics
    m_total_number = 0;
    m_total_type_number = 0;
    m_mrr = 0.0;
    m_top1_correct = 0;
    m_top5_correct = 0;
    m_top10_correct = 0;
    m_total_prob = 0.0;

    //Default type subsetting treats the list of types as inclusive rather than exclusive.
    invertTypes = false;

    if(strcmp(Data::SPLIT_FILE.c_str(), "") != 0)
    {
        //TODO: read in the split file (format 1 type per line)
        ifstream fin(Data::SPLIT_FILE.c_str());
        string line;
        while (getline(fin, line))
        {
            if(line.compare("Invert") == 0)
 	    {
                cout << "Inverting." << endl;
                invertTypes = true;
		continue;
            }
            cout << "<" << line << ">" << endl;
            consideredTypes.push_back(line);
        }
    }
    
    if (Data::DEBUG)
    {
        m_fout.open(Data::OUTPUT_FILE.c_str());
    }

    if (Data::FILES)
    {
        DealFiles();
    }
    else
    {
        DealFile(Data::INPUT_FILE);
    }
    //cout << "Total tokens: " << m_total_number << endl;
    if (Data::ENTROPY)
    {
	cout << Data::INPUT_FILE << endl;
        //If we aren't spliting by type, consider all tokens in the file.
        if(strcmp(Data::SPLIT_FILE.c_str(), "") == 0)
        {
            cout << "Total tokens: " << m_total_number << endl;
            cout << "Sum: " << -m_total_prob << endl;
            cout << "Entropy: " << -m_total_prob/m_total_number << endl;
        }
        else
        {
	    cout << "Total tokens: " << m_total_type_number << endl;
            cout << "Sum: " << -m_total_prob << endl;
            cout << "Entropy: " << -m_total_prob/m_total_type_number << endl;
        }
    }
    else
    {
        cout << "Mean reciprocal rank: " << m_mrr/m_total_number << endl;
        cout << "Total top1 accuracy: " << (float)m_top1_correct/m_total_number << endl;
        cout << "Total top5 accuracy: " << (float)m_top5_correct/m_total_number << endl;
        cout << "Total top10 accuracy: " << (float)m_top10_correct/m_total_number << endl;
    }
}

void Suggestion::DealFiles()
{
    vector<string> input_files;
    ifstream fin(Data::INPUT_FILE.c_str());
    string line;
    while (getline(fin, line))
    {
        input_files.push_back(line);
    }
    fin.close();

    ifstream fin_list(Data::INPUT_FILE.c_str());

    ofstream fout_file_measures((Data::INPUT_FILE+".file.measures").c_str());

    ifstream fin_scope_list;
    if (Data::USE_RELATED_FILE)
    {
        fin_scope_list.open(Data::SCOPE_FILE.c_str());
    }

    string file_name;
    string scope_file_name;
    while (getline(fin_list, file_name))
    {
        ifstream fin(file_name.c_str());
        getline(fin_scope_list, scope_file_name);
        ReadScope(scope_file_name);

        if (Data::USE_RELATED_FILE)
        {
            for (int i=0; i<(int)m_related_files.size(); ++i)
            {
                Data::CACHE.Build(Data::FILE_DIR + "/" + m_related_files.at(i), Data::CACHE_ORDER);
                if (Data::DEBUG)
                {
                    cout << "related file: " << Data::FILE_DIR + "/" + m_related_files.at(i) << endl;
                    cout << "cache: " << Data::CACHE.m_records.size() << endl;
                }
            }
        }

        DealFile(file_name);

        if (Data::USE_FILE_CACHE)
        {
            Data::CACHE.Clear();
        }

        if (Data::ENTROPY)
        {
           fout_file_measures << -m_file_prob/m_file_total_number << endl;
        }
        else
        {
            fout_file_measures << m_file_mrr/m_file_total_number << " ||| "
                               << (float)m_file_top1_correct/m_file_total_number << " ||| "
                              << (float)m_file_top5_correct/m_file_total_number << " ||| "
                               << (float)m_file_top10_correct/m_file_total_number << endl;
        }
    }

}

void Suggestion::DealFile(const string& input_file)
{
    //cout << "ON File: " << input_file << endl;
    // initilize the statistics for each file
    m_file_total_number = 0;
    m_file_mrr = 0.0;
    m_file_top1_correct = 0;
    m_file_top5_correct = 0;
    m_file_top10_correct = 0;
    m_file_prob = 0.0;

    // get the tokens of the input file
    vector<string> tokens;
    tokens.push_back("<s>");
    
    ifstream fin(input_file.c_str());
    string line, token;
    while (getline(fin, line))
    {
        stringstream ss(line);

        while (ss >> token)
        {
            tokens.push_back(token);
        }
    }


    //Check if metadata file exists and read in project and file name
    vector<string> pieces;
    Split(input_file, ".", pieces);
    string meta_file = pieces[0] + "." + pieces[1] + ".metadata";
    vector<string> metaInfo; //project, file
    if (Data::DEBUG)
    {
    	if(file_exists(meta_file))
    	{
            ifstream metaIn(meta_file.c_str());
            string line, nextInfo;
            getline(metaIn, line);
            stringstream ss(line);
            for(int i = 0; i < 2; i++) //Only need first 2 tokens
            {
                ss >> nextInfo;
                metaInfo.push_back(nextInfo);   
            }
            metaIn.close();
    	}
    }

    // analysis the tokens
    // common usage
    string prefix, cache_prefix;
    string debug_info;
    int start;

    // for predicting task
    vector<Word> candidates;
    int rank;

    // for calculating the cross entropy
    float prob;

    for (int i=1; i<(int)tokens.size(); i++)
    {
        start = i-(Data::NGRAM_ORDER-1)>0? i-(Data::NGRAM_ORDER-1) : 0;
        Join(tokens, start, i-1, prefix);
        
        if (Data::USE_CACHE)
        {
            // generate new prefix for cache
            start = i-(Data::CACHE_ORDER-1)>0 ? i-(Data::CACHE_ORDER-1) : 0;
            Join(tokens, start, i-1, cache_prefix);
        }

        if (Data::ENTROPY)
        {
            //Get the probability of the next token.
            prob = GetProbability(prefix, cache_prefix, tokens.at(i), debug_info);
            //If we aren't spliting by type, consider all tokens in the file.
            if(strcmp(Data::SPLIT_FILE.c_str(), "") == 0)
            { 
                m_file_prob += prob;
            }
            else //We want to average over only the tokens of the right type
            {
                if(isConsideredType(tokens.at(i), consideredTypes) != invertTypes) //Xor on the types
                {
                    m_file_prob += prob;
                    //Keep running sum of thing to average on.
                    m_total_type_number++;
                }
           	}

            //Print Debug information (NOTE THIS BEHAVES DIFFERENTLY FOR CODE COMPARISONS.)
            if (Data::DEBUG)
            {
             	/*if(metaInfo.empty())
				{
                	m_fout << "<bead>" << endl;
                 	m_fout << "<ref> " << tokens.at(i) << " </ref>" << endl;
                 	m_fout << "<prob> " << prob << " ||| " << debug_info << " </prob>" << endl;
                 	m_fout << "</bead>" << endl;
				}
				else //Produce a csv style entry
				{*/
					//m_fout << metaInfo[0] << "," << metaInfo[1] << "," << input_file.c_str() << "," << i-1 << ",\"" << tokens.at(i) << "\"," << prob << endl;
                      m_fout << input_file.c_str() << "," << i-1 << ",\"" << tokens.at(i) << "\"," << prob << endl;
				//}
        	}
        }
        else
        {
            GetCandidates(prefix, cache_prefix, candidates);
            // for calcuting accuracy
            rank= GetRank(candidates, tokens.at(i));
            if (rank > 0)
            {
                m_file_mrr += 1/(float)rank;
            }
            m_file_top1_correct += Is_in(candidates, tokens.at(i), 1);
            m_file_top5_correct += Is_in(candidates, tokens.at(i), 5);
            m_file_top10_correct += Is_in(candidates, tokens.at(i), 10);
      
            if (Data::DEBUG)
            {
                m_fout << "<bead>" << endl;
                m_fout << "<ref>" << tokens.at(i) << "</ref>" << endl;
                for (int j=0; j<(int)candidates.size(); j++)
                {
                    if (j == 10)
                    {
                        break;
                    }

                    m_fout << "<cand id=" << j+1 << "> " 
                           << candidates.at(j).m_token << " ||| " << candidates.at(j).m_prob 
                           << " ||| " << candidates.at(j).m_debug
                           << " </cand>" << endl;
                }
                m_fout << "</bead>" << endl;
            }
        }
         
        // update the cache
        if (Data::USE_CACHE)
        {
            if (Data::USE_WINDOW_CACHE)
            {
                Data::CACHE.Update(cache_prefix, tokens.at(i), Data::WINDOW_SIZE);
            }
            else
            {
                Data::CACHE.Update(cache_prefix, tokens.at(i));
            }
        }
    }
    
    int num = (int)tokens.size() - 1;
    m_file_total_number = num;
    m_total_number += m_file_total_number;
    
    if (Data::ENTROPY)
    {
        // calcuting the cross entropy
        m_total_prob += m_file_prob;
    }
    else
    {
        // calcuting accuracy
        m_mrr += m_file_mrr;
        m_top1_correct += m_file_top1_correct;
        m_top5_correct += m_file_top5_correct;
        m_top10_correct += m_file_top10_correct;
    }
}



void Suggestion::GetCandidates(const string& prefix,
                               const string& cache_prefix,
                               vector<Word>& candidates)
{
    if (!Data::USE_CACHE_ONLY)
    {
        // n-gram word candidates
        Data::NGRAM->GetCandidates(prefix, Data::USE_BACKOFF, candidates);
        if (Data::DEBUG)
        {
            for (int i=0; i<(int)candidates.size(); ++i)
            {
                candidates.at(i).m_debug = "ngram prob: " + double_to_string(candidates.at(i).m_prob);
            }
        }
    }
    else
    {
        candidates.clear();
    }

    if (Data::USE_CACHE)
    {
        // update the candidates according to the cache
        Data::CACHE.UpdateCandidates(cache_prefix, Data::CACHE_LAMBDA, Data::CACHE_DYNAMIC_LAMBDA, candidates);
    }
}


float Suggestion::GetProbability(const string& prefix, 
                                 const string& cache_prefix, 
                                 const string& token, 
                                 string& debug_info)
{
    float prob = 0.0;
    debug_info.clear();

    if (!Data::USE_CACHE_ONLY)
    {
        prob = Data::NGRAM->GetProbability(prefix, token, Data::USE_BACKOFF);
        if (Data::DEBUG)
        {
            debug_info = "ngram prob: " + double_to_string(pow(2, prob));
        }
    }

    if (Data::USE_CACHE)
    {
        int cache_count = Data::CACHE.GetCount(cache_prefix);
        if (cache_count != 0)
        {
            float cache_discount = Data::CACHE_LAMBDA;
            if (Data::CACHE_DYNAMIC_LAMBDA)
            {
                //P(cnd) = 1/(cache_count+1)*P(lm) + cache_count/(cache_count+1)*P(cache)
                cache_discount = (float)cache_count/(cache_count+1);
            }

            float ngram_discount = 1-cache_discount;

            int ngram_count = Data::CACHE.GetCount(cache_prefix, token);
            prob = ngram_discount * pow(2, prob) + cache_discount * ((float)ngram_count/cache_count);
            debug_info += ", in cache: " + int_to_string(ngram_count) + "/" + int_to_string(cache_count);
            
            if (prob > 0.0)
            {   //Noticed this behavior in 4 and 5 grams. (in both cache and no cache model, doesn't appear in trigrams for either?)
                prob = log2(prob); //Can be positive or negative, what about if prob > 1?  Is this not being calculated correctly?
            }
            else
            {
                prob = Data::NGRAM->m_unk_prob;
            }
        }
    }

    if(prob > 0.0)
    {
        cout << "Error found in Suggestion.cpp" << endl;
        cout << "Prefix: " << prefix << endl;
        cout << "Cache prefix: " << cache_prefix << endl;
        cout << "Token: " << token << endl;
        cout << "Probability: " <<prob << endl;
	}

    return prob;
}


int Suggestion::GetRank(const vector<Word>& candidates, const string& ref)
{
    for (int i=0; i<(int)candidates.size(); i++)
    {
        if (candidates.at(i).m_token == ref)
        {
            return i+1;
        }
    }

    return 0;
}

int Suggestion::Is_in(const vector<Word>& candidates, const string& ref, const int top_n)
{
    int end = top_n < candidates.size() ? top_n : candidates.size();
    for (int i=0; i<end; i++)
    {
        if (candidates.at(i).m_token == ref)
        {
            return 1;
        }
    }

    return 0;
}

void Suggestion::ReadScope(const string& scope_file_name)
{
    m_class_scope_begins.clear();
    m_class_scope_ends.clear();
    m_method_scope_begins.clear();
    m_method_scope_ends.clear();
    m_related_files.clear();

    ifstream fin(scope_file_name.c_str());
    string line;

    vector<string> items;

    while (getline(fin, line))
    {
        if (startswith(line, "<class>"))
        {
            while (getline(fin, line))
            {
                if (startswith(line, "</class>"))
                {
                    break;
                }

                Split(line, items);
                m_class_scope_begins.insert(atoi(items.at(0).c_str()));
                m_class_scope_ends.insert(atoi(items.at(1).c_str()));
            }
        }
        if (startswith(line, "<method>"))
        {
            while (getline(fin, line))
            {
                if (startswith(line, "</method>"))
                {
                    break;
                }

                Split(line, items);
                m_method_scope_begins.insert(atoi(items.at(0).c_str()));
                m_method_scope_ends.insert(atoi(items.at(1).c_str()));
            }
        }
        if (startswith(line, "<file>"))
        {
            while (getline(fin, line))
            {
                if (startswith(line, "</file>"))
                {
                    break;
                }

                m_related_files.push_back(line);
            }
        }
    }
}

Word Suggestion::selectCandidate(const vector<Word>& candidates, const vector<float>& probs)
{
    //Generate random number between 0 and 1
    //Map to a suggestion.
    float select = getRandom();
    cout << "Random value: " << select << endl;
    float threshold = 0;
    for(int i=0; i < candidates.size(); i++)
    {
        threshold += probs[i];
        if(select < threshold)
        {
            return candidates[i];
        }
    }
    return candidates[candidates.size()-1];
}