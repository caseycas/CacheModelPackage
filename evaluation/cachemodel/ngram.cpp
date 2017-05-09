#include "ngram.h"


//Error: the ngram base map is not actually loaded in ever?
Ngram::Ngram(const string& ngramFile,
             const int order,
             const int beam_size)
{
    // we ingore the 1-grams, because 1-grams give no prefix
    // we may improve this in the future
    m_ngrams_list.resize(order);

    ifstream fin(ngramFile.c_str());
    /**
    
    **/

    cout << "=================================================" << endl;
    cout << "Reading ngrams..." << endl;

    string line;
    vector<string> items;
    vector<Word> words;
    string prefix, last_prefix;
    int n = -1;
    while (getline(fin, line))
    {
        if (endswith(line, "-grams:"))
        {
            if (n > 0)
            {
                cout << n << "/" << order << " finished." << endl;
				cout << words.size() << " words processed." << endl;
            }
            // push the words into the list, before changing the "n"
            if (!words.empty())
            {
               // sort the words according to their probabilities
               sort(words.rbegin(), words.rend());
               if (words.size() > beam_size)
               {
                   words.resize(beam_size);
               }
               m_ngrams_list.at(n-1).insert(make_pair(last_prefix, words));
            }
            // here we don't need to update the last prefix
            // because when "n" changes, the prefix must be different
            words.clear();

           // read the n of the current grams
           n = atoi(line.substr(1, line.size()-8).c_str());
        }
        else
        {
            Split(line, "\t", items);
            if (items.size() > 1)
            {
                Word word;
                word.m_prob = atof(items.at(0).c_str());

                if (items.size() > 2)
                {
                    // back-off penalty
                    word.m_prob += atof(items.at(2).c_str());
                }

                word.m_prob = pow(10, word.m_prob);

                GetFirstNWords(items.at(1), n-1, prefix);
                GetLastNWords(items.at(1), 1, word.m_token);
                if (prefix == last_prefix)
                {
                    words.push_back(word);
                }
                else
                {
                    if (!words.empty())
                    {
                       // sort the words according to their probabilities
                       sort(words.rbegin(), words.rend());
                       if (words.size() > beam_size)
                       {
                           words.resize(beam_size);
                       }
                       m_ngrams_list.at(n-1).insert(make_pair(last_prefix, words));
                    }

                    last_prefix = prefix;
                    words.clear();
                    words.push_back(word);
                }
            }
        }
    }
    
    if (!words.empty())
    {
       m_ngrams_list.at(n-1).insert(make_pair(last_prefix, words));
    }
    
    cout << n << "/" << order << " finished." << endl;

    //Print the whole thing out.
    /*for(vector<map<string, vector<Word> > >::iterator it = m_ngrams_list.begin(); it != m_ngrams_list.end(); ++it)
    {
        map<string, vector<Word> > ngram_vector = *it;
	for(map<string, vector<Word> >::iterator it2 = ngram_vector.begin(); it2 != ngram_vector.end(); ++it2)
	{
                prefix = it2->first;
                for(vector<Word>::iterator it3 = it2->second.begin(); it3 != it2->second.end(); ++it3)
		{
			cout << "Prefix :" << prefix << " Word: " << it3->m_token << " Prob: " << it3->m_prob << endl;
		}
	}
    }*/
}

bool Ngram::GetCandidates(const std::string& prefix, const bool use_backoff, vector<Word>& candidates)
{
    candidates.clear();

    int n = CountWords(prefix);
    // here n is the number of grams in the prefix, the real "n" should be n+1
    // therefore, here we use "n" rather than "n-1"
    cout << "Ngram List size: " << m_ngrams_list.size() << endl;
    map<string, vector<Word> >& ngram_map = m_ngrams_list.at(n);

    map<string, vector<Word> >::iterator iter = ngram_map.find(prefix);
    cout << "Ngram Map size: " << ngram_map.size() << endl;
    if (iter != ngram_map.end())
    {
        cout << "Found in map\n"; 
        candidates = iter->second;
        return true;
    }
    else
    {
        cout << "Using backoff\n";
        if (use_backoff)
        {
            if (n < 1)
            {
                // when n is less or equal to 1, we cannot do the back-off operation
                return false;
            }

            string use_backoff_prefix;
            GetLastNWords(prefix, n-1, use_backoff_prefix);

            return GetCandidates(use_backoff_prefix, use_backoff, candidates);
        }
        else
        {
            return false;
        }
    }
}


Ngram::Ngram(const string& ngramFile,
             const int order)
{
    // we ingore the 1-grams, because 1-grams give no prefix
    // we may improve this in the future
    m_ngrams_map.resize(order);

    ifstream fin(ngramFile.c_str());
    /**
    
    **/

    cout << "=================================================" << endl;
    cout << "Reading ngrams..." << endl;

    string line;
    vector<string> items; // Splits up the 3 part line.
    map<string, float> words;
    string prefix, last_prefix, token;
    float prob;
    int n = -1;
    int lines = 0;
    int added = 0;
    int words_added = 0;
    while (getline(fin, line))
    {
        if (endswith(line, "-grams:"))
        {
            if (n > 0)
            {
                cout << n << "/" << order << " finished." << endl;
            }
            // push the words into the list, before changing the "n"
            if (!words.empty())
            {
               words_added += words.size();         
               if(m_ngrams_map.at(n-1).find(last_prefix) != m_ngrams_map.at(n-1).end())
               {
                  //cout << "Prefix overwritten: " << last_prefix << endl;
                  m_ngrams_map.at(n-1).find(last_prefix)->second.insert(words.begin(), words.end());
               }
               else
	       {
               // sort the words according to their probabilities
               m_ngrams_map.at(n-1).insert(make_pair(last_prefix, words));
               }
            }

            // here we don't need to update the last prefix
            // because when "n" changes, the prefix must be different
            words.clear();

           // read the n of the current grams
           n = atoi(line.substr(1, line.size()-8).c_str());
        }
        else 
        {
            Split(line, "\t", items);
            if (items.size() > 1)
            {
                lines++;
                prob = atof(items.at(0).c_str()); 

                if (items.size() > 2)
                {
	
                	/*if(atof(items.at(2).c_str()) > 0.0)
					{
						cout << "Positive discount." << endl;
						cout << items.at(0).c_str() << " " << items.at(1).c_str() << " " << items.at(2).c_str() << endl; 
					}
                    else
					{*/
                    // back-off penalty
                    prob += atof(items.at(2).c_str());
					//}
                }

                // word.m_prob = pow(10, word.m_prob);
                prob = prob * LOG_2_10; //Prob used is 1 + 3rd (times base 2 log of 10?)
 
                GetFirstNWords(items.at(1), n-1, prefix);
                GetLastNWords(items.at(1), 1, token);

                //Then assign to the word with associated prefix?
                if (prefix == last_prefix)
                {
                    added++;
                    words[token] = prob;
                }
                else
                {
                    if (!words.empty())
                    {

                        words_added += words.size();
                        if(m_ngrams_map.at(n-1).find(last_prefix) != m_ngrams_map.at(n-1).end())
                        {
                           	//cout << "Prefix overwritten: " << last_prefix << endl;
                  		m_ngrams_map.at(n-1).find(last_prefix)->second.insert(words.begin(), words.end());
                  	}
               		else
               		{
              			// sort the words according to their probabilities 
               			m_ngrams_map.at(n-1).insert(make_pair(last_prefix, words));
               		}
                    }

                    last_prefix = prefix;
                    words.clear();
                    added++;
                    words[token] = prob;
                }
            }
        }
    }
    
    if (!words.empty())
    {
        words_added += words.size();
        if(m_ngrams_map.at(n-1).find(last_prefix) != m_ngrams_map.at(n-1).end())
        {
                  //cout << "Prefix overwritten: " << last_prefix << endl;
                  m_ngrams_map.at(n-1).find(last_prefix)->second.insert(words.begin(), words.end());
        }
        else
        {
                  // sort the words according to their probabilities 
                  m_ngrams_map.at(n-1).insert(make_pair(last_prefix, words));
        }
    }
    
    cout << n << "/" << order << " finished." << endl;
    //Vincent is pointing out that this is the source of the 10 entropy spike and that
    //a more correct one should be the binary log of the vocab at a point in time.
    //Something to fix maybe -> talk to Vincent tomorrow.
    m_unk_prob = -10;
    map<string, float>::iterator iter = m_ngrams_map.at(0)[""].find("<unk>");
    if (iter != m_ngrams_map.at(0)[""].end())
    {
        m_unk_prob = iter->second;
    }
    /*
    cout << "Ngram Lines Hit: " << lines << " Ngram Lines Added: " << added << endl;
    cout << "Ngram max size: " << m_ngrams_map.size() << endl;
    //std::vector<string, map<string, float > >::iterator it = m_ngrams_map.begin();
    //Print the whole thing out.
   
    for(int i = 0; i < order; ++i)
    {
        cout << m_ngrams_map.at(i).size()<< endl;
        for(map<string, map<string, float> >::iterator it = m_ngrams_map.at(i).begin(); it !=  m_ngrams_map.at(i).end(); ++it)
        {
		prefix = it->first;
                for(map<string, float>::iterator it2 = it->second.begin(); it2 != it->second.end(); ++it2)
        	{
                	 cout << "Prefix: " << prefix << " Word: " << it2->first << " Prob: " << it2->second << endl;
        	}
	}
        
        prefix = m_ngrams_map.at(i).first;
        map<string, float> ngram_vector = m_ngrams_map.at(i).second;
        cout << "Ngram list length: " << ngram_vector.size() << endl;
        for(map<string, float>::iterator it2 = ngram_vector.begin(); it2 != ngram_vector.end(); ++it2)
        {
        	 cout << "Prefix :" << prefix << " Word: " << it2->first << " Prob: " << it2->second << endl;
        }
       
    }*/
}

//This seems to be rarely producing strange values in 4 and 5 grams.  I'm not sure I trust it.
//Occurs in backoff.
float Ngram::GetProbability(const string& prefix, const string& token, const bool use_backoff)
{   
    int n = CountWords(prefix);
    // here n is the number of grams in the prefix, the real "n" should be n+1
    // therefore, here we use "n" rather than "n-1"
    map<string, map<string, float> >& ngram_map = m_ngrams_map.at(n);
    map<string, map<string, float> >::iterator iter = ngram_map.find(prefix);
    if (iter != ngram_map.end())
    {
        map<string, float>::iterator iter1 = iter->second.find(token);
        if (iter1 != iter->second.end())
        {
            /*if(iter1->second > 1.0)
			{
                cout << "Found error in Ngram.cpp." << endl;
                cout << "Prefix: " << prefix << endl;
				cout << "Token: " << iter1->first << endl;
                float tmp = iter1->second;
                cout << "Probability: " << tmp << endl;
			}*/
            return iter1->second;
        }
    }

    // no record is found
    if (use_backoff)
    {
        if (n == 0)
        {
            return m_unk_prob;
        }

        string backoff_prefix;
        GetLastNWords(prefix, n-1, backoff_prefix);

        return GetProbability(backoff_prefix, token, use_backoff);
    }
    
    // the default value for the unknow n-grams
    return m_unk_prob;
}
