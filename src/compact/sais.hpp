#pragma once
#include <algorithm>
#include <cassert>
#include <climits>
#include <string>
#include <vector>
using namespace std;

// Induced sorting adapted from ACL string.hpp, CC0-1.0,
// commit 864245a00b00dd008d1abfdc239618fdb7d139da.
// BEGIN SAIS
struct SAIS
{
    vector<int> sa, rk, lcp;

    SAIS(const string &s)
    {
        assert(s.size() < INT_MAX);
        vector<int> a;
        a.reserve(s.size());
        for (unsigned char c : s) a.push_back(c);
        *this = SAIS(a, 256);
    }

    SAIS(const vector<int> &s, int alphabet)
    {
        assert(s.size() < INT_MAX && 1 <= alphabet && alphabet < INT_MAX);
        for (int c : s) assert(0 <= c && c < alphabet);
        int n = s.size();
        sa = sort_suffixes(s, alphabet);
        rk.resize(n);
        lcp.assign(n, 0);
        for (int i = 0; i < n; i++) rk[sa[i]] = i;
        for (int i = 0, k = 0; i < n; i++)
        {
            if (!rk[i])
            {
                k = 0;
                continue;
            }
            int j = sa[rk[i] - 1];
            while (k < n - i && k < n - j && s[i + k] == s[j + k]) k++;
            lcp[rk[i]] = k;
            if (k) k--;
        }
    }

private:
    static vector<int> sort_suffixes(const vector<int> &s, int alphabet)
    {
        int n = s.size();
        if (!n) return {};
        if (n == 1) return {0};
        vector<int> sa(n), lo(alphabet + 1), hi(alphabet + 1);
        vector<bool> type(n);
        for (int i = n - 2; i >= 0; i--)
            type[i] = s[i] == s[i + 1] ? type[i + 1] : s[i] < s[i + 1];
        for (int i = 0; i < n; i++)
            if (type[i]) lo[s[i] + 1]++;
            else hi[s[i]]++;
        for (int c = 0; c < alphabet; c++)
        {
            hi[c] += lo[c];
            lo[c + 1] += hi[c];
        }
        auto induce = [&](const vector<int> &lms)
        {
            fill(sa.begin(), sa.end(), -1);
            vector<int> pos = hi;
            for (int i : lms) sa[pos[s[i]]++] = i;
            pos = lo;
            sa[pos[s[n - 1]]++] = n - 1;
            for (int i = 0; i < n; i++)
            {
                int v = sa[i];
                if (v > 0 && !type[v - 1]) sa[pos[s[v - 1]]++] = v - 1;
            }
            pos = lo;
            for (int i = n - 1; i >= 0; i--)
            {
                int v = sa[i];
                if (v > 0 && type[v - 1]) sa[--pos[s[v - 1] + 1]] = v - 1;
            }
        };
        vector<int> id(n, -1), lms;
        for (int i = 1; i < n; i++)
            if (!type[i - 1] && type[i])
            {
                id[i] = lms.size();
                lms.push_back(i);
            }
        induce(lms);
        int m = lms.size();
        if (m)
        {
            vector<int> order, reduced(m);
            for (int v : sa)
                if (id[v] >= 0) order.push_back(v);
            int names = 1;
            for (int i = 1; i < m; i++)
            {
                int a = order[i - 1], b = order[i];
                int x = id[a] + 1 < m ? lms[id[a] + 1] : n;
                int y = id[b] + 1 < m ? lms[id[b] + 1] : n;
                bool same = x - a == y - b;
                if (same)
                {
                    while (a < x && s[a] == s[b]) a++, b++;
                    same = a < n && b < n && s[a] == s[b];
                }
                if (!same) names++;
                reduced[id[order[i]]] = names - 1;
            }
            order = sort_suffixes(reduced, names);
            for (int &i : order) i = lms[i];
            induce(order);
        }
        return sa;
    }
};
// END SAIS
