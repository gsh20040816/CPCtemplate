#pragma once
#include "string.hpp"

// BEGIN ACWeighted
struct ACWeighted
{
    AhoCorasick ac;
    vector<long long> sum;

    ACWeighted(const vector<pair<string, long long>> &patterns = {})
    {
        vector<pair<int, long long>> ends;
        for (const auto &[s, w] : patterns)
        {
            int u = s.empty() ? 0 : ac.add(s);
            ends.push_back({u, w});
        }
        ac.build();
        sum.resize(ac.a.size());
        for (auto [u, w] : ends) sum[u] += w;
        for (int u : ac.order) sum[u] += sum[ac.a[u].fail];
    }

    long long query(const string &s) const
    {
        long long ans = sum[0];
        int u = 0;
        for (char c : s)
        {
            assert('a' <= c && c <= 'z');
            u = ac.a[u].go[c - 'a'];
            ans += sum[u];
        }
        return ans;
    }
};

// END ACWeighted

// BEGIN DynamicAC
struct DynamicAC
{
    vector<vector<pair<string, long long>>> block;
    vector<ACWeighted> ac;

    void add(string s, long long w)
    {
        vector<pair<string, long long>> cur;
        cur.push_back({move(s), w});
        int k = 0;
        while (k < (int)block.size() && !block[k].empty())
        {
            for (auto &p : block[k]) cur.push_back(move(p));
            block[k].clear();
            ac[k] = ACWeighted();
            k++;
        }
        if (k == (int)block.size())
        {
            block.emplace_back();
            ac.emplace_back();
        }
        block[k] = move(cur);
        ac[k] = ACWeighted(block[k]);
    }

    long long query(const string &s) const
    {
        long long ans = 0;
        for (int k = 0; k < (int)block.size(); k++)
        {
            if (!block[k].empty()) ans += ac[k].query(s);
        }
        return ans;
    }
};

// END DynamicAC
