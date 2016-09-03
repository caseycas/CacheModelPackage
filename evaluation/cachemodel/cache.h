#ifndef __CACHE_H__
#define __CACHE_H__
#include <string>
#include <iostream>
#include <fstream>
#include <vector>
#include <queue>
#include <ctime>

#include "utility.h"
#include "ngram.h"

using namespace std;

class Record
{
public:
    Record()
    {
        m_count = 0;
    }

    Record(const string& token)
    {
        m_tokens.insert(make_pair(token, 1));
        m_count = 1;
    }

    void Update(const string& token)
    {
        m_count += 1;
        map<string, int>::iterator iter = m_tokens.find(token);
        if (iter != m_tokens.end())
        {
            iter->second += 1;
        }
        else
        {
            m_tokens.insert(make_pair(token, 1));
        }
    }

    void Delete(const string& token)
    {
        m_count -= 1;
        map<string, int>::iterator iter = m_tokens.find(token);
        if (iter != m_tokens.end())
        {
            iter->second -= 1;
        }

        if (iter->second == 0)
        {
            m_tokens.erase(iter);
        }
    }

    int Find(const string& token)
    {
        map<string, int>::iterator iter = m_tokens.find(token);
        if (iter != m_tokens.end())
        {
            return iter->second;
        }
        else
        {
            return 0;
        }
    }

    int GetCount()
    {
        return m_count;
    }

    void GetTokenCounts(map<string, int>& token_counts)
    {
        token_counts = m_tokens;
    }
protected:
    // the count of the prefix: C(wi-2 wi-1)
    int m_count;
private:
    // the map of tokens that occur after the prefix, as well as their counts
    map<string, int> m_tokens;
};

class Cache
{
public:
    Cache()
    {
        m_min_order = 3;
    }
    void SetMinOrder(const int order)
    {
        m_min_order = order;
    }
    /**
    * update the cache with the record (prefix, token)
    * @param prefix       the previous (n-1) tokens
    * @param token        the current token
    **/

    void Build(const string& input_file, const int cache_order)
    {
        vector<string> tokens;
        tokens.push_back("<s>");

        ifstream fin(input_file.c_str());
        string line;
        string token, cache_prefix;

        while (getline(fin, line))
        {
            stringstream ss(line);

            while (ss >> token)
            {
                tokens.push_back(token);
            }
        }
        
        for (int i=m_min_order-1; i<(int)tokens.size(); i++)
        {
            int start = i-(cache_order-1) > 0? i-(cache_order-1) : 0;

            Join(tokens, start, i-1, cache_prefix);

            Update(cache_prefix, tokens.at(i));
        }
    }

    void Update(const string& prefix, const string& token)
    {
        int n = CountWords(prefix);
        string new_prefix;
        for (int i=n; i>=m_min_order-1; --i)
        {
            GetLastNWords(prefix, i, new_prefix);
            map<string, Record>::iterator iter = m_records.find(new_prefix);
            if (iter != m_records.end())
            {
                iter->second.Update(token);
            }
            else
            {
                Record record(token);
                m_records.insert(make_pair(new_prefix, record));
            }
        }
    }
    
    /**
    * update the cache with the record (prefix, token)
    * @param prefix       the previous (n-1) tokens
    * @param token        the current token
    * @param window_size  the size of window for window cache
    **/
    void Update(const string& prefix, const string& token, const int window_size)
    {
        Update(prefix, token);

        // maintaining the cache window
        m_cache_queue.push(make_pair(prefix, token));

        if ((int)m_cache_queue.size() > window_size)
        {
            pair<string, string> to_delete = m_cache_queue.front();
            m_cache_queue.pop();

            Delete(to_delete.first, to_delete.second);
        }
    }

    void Delete(const string& prefix, const string& token)
    {
        int n = CountWords(prefix);
        string new_prefix;
        for (int i=n; i>=m_min_order-1; --i)
        {
            GetLastNWords(prefix, i, new_prefix);
            m_records[new_prefix].Delete(token);
            if (m_records[new_prefix].GetCount() == 0)
            {
                m_records.erase(m_records.find(new_prefix));
            }
        }
    }

    void Clear()
    {
        m_records.clear();
    }

    void UpdateCandidates(const string& prefix, const float cache_lambda, const bool cache_dynamic_lambda, vector<Word>& candidates)
    {
        int cache_count = GetCount(prefix);
        if (cache_count != 0)
        {
            int valid_order = GetValidOrder(prefix);
            float cache_discount = cache_lambda;
            if (cache_dynamic_lambda)
            {
                //P(cnd) = 1/(cache_count+1)*P(lm) + cache_count/(cache_count+1)*P(cache)
                cache_discount = (float)cache_count/(cache_count+1);
            }
            float ngram_discount = 1-cache_discount;

            // found cache records of the prefix
            map<string, int> token_counts;
            GetTokenCounts(prefix, token_counts);

            // update the information of candidates get by the ngrams
            map<string, int>::iterator iter;
            for (int i=0; i<(int)candidates.size(); ++i)
            {
                // discount the probability first
                candidates.at(i).m_prob *= ngram_discount;

                iter = token_counts.find(candidates.at(i).m_token);
                if (iter != token_counts.end())
                {
                    candidates.at(i).m_prob += cache_discount * ((float)iter->second/cache_count);
                    candidates.at(i).m_debug += ", in cache with order " + to_string(valid_order) + " : " + to_string(iter->second) + "/" + to_string(cache_count);
                    token_counts.erase(candidates.at(i).m_token);
                }
            }

            // add the left records in the cache to te candidates
            for (iter=token_counts.begin(); iter!=token_counts.end(); ++iter)
            {
                Word candidate(iter->first, cache_discount * ((float)iter->second/cache_count));
                candidate.m_debug += "only in cache with order " + to_string(valid_order) + " : " + to_string(iter->second) + "/" + to_string(cache_count);
                candidates.push_back(candidate);
            }

            // sort the candidates, because the scores are changed
            sort(candidates.rbegin(), candidates.rend());
        }
    }

    void GetTokenCounts(const string& prefix, map<string, int>& token_counts)
    {
        token_counts.clear();
        
        int n = CountWords(prefix);
        string new_prefix;
        for (int i=n; i>=m_min_order-1; --i)
        {
            GetLastNWords(prefix, i, new_prefix);

            map<string, Record>::iterator iter = m_records.find(new_prefix);
            if (iter != m_records.end())
            {
                iter->second.GetTokenCounts(token_counts);
                break;
            }
        }
    }

    int GetValidOrder(const string& prefix)
    {
        int n = CountWords(prefix);
        string new_prefix;
        for (int i=n; i>=m_min_order-1; --i)
        {
            GetLastNWords(prefix, i, new_prefix);

            map<string, Record>::iterator iter = m_records.find(new_prefix);
            if (iter != m_records.end())
            {
                return i+1;
            }
        }
    }

    int GetCount(const string& prefix)
    {
        int n = CountWords(prefix);
        string new_prefix;
        for (int i=n; i>=m_min_order-1; --i)
        {
            GetLastNWords(prefix, i, new_prefix);

            map<string, Record>::iterator iter = m_records.find(new_prefix);
            if (iter != m_records.end())
            {
                return iter->second.GetCount();
            }
        }

        return 0;
    }
    
    int GetCount(const string& prefix, const string& token)
    {
        int n = CountWords(prefix);
        string new_prefix;
        for (int i=n; i>=m_min_order-1; --i)
        {
            GetLastNWords(prefix, i, new_prefix);

            map<string, Record>::iterator iter = m_records.find(new_prefix);
            if (iter != m_records.end())
            {
                int count = iter->second.Find(token);

                if (count != 0)
                {
                    return count;
                }
            }
        }

        return 0;
    }

    map<string, Record> m_records;
private:
    // the map that contains the records given a prefix (e.g., wi-2 wi-1)
    int m_min_order;
    queue<pair<string, string> > m_cache_queue;
};
#endif

