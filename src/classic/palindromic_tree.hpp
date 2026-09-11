#pragma once
#include <cassert>
#include <vector>
using namespace std;

template <int N> struct Palindromic_Tree
{
    struct Node
    {
        int next[26]{};
        int len = 0, fail = 0, suffixes = 0, end = -1;
        long long hits = 0;
    };

    Node t[N + 2];
    int tot = 1;
    vector<int> s;
    int last = 0;
    long long total = 0;

    void Init()
    {
        tot = 1;
        t[0] = Node{};
        t[1] = Node{};
        t[0].fail = 1;
        t[1].len = -1;
        s.assign(1, -1);
        last = 0;
        total = 0;
    }

    int Get_Fail(int u) const
    {
        int pos = s.size() - 1;
        while ( s[pos - t[u].len - 1] != s[pos] )
            u = t[u].fail;
        return u;
    }

    // Append a lowercase letter; return the longest palindromic suffix node.
    int Insert(char ch)
    {
        int c = ch - 'a';
        assert(0 <= c && c < 26);
        assert(s.size() <= N);
        s.push_back(c);
        int u = Get_Fail(last);
        if ( !t[u].next[c] )
        {
            int v = ++tot;
            t[v] = Node{};
            t[v].len = t[u].len + 2;
            t[v].fail = t[Get_Fail(t[u].fail)].next[c];
            t[v].suffixes = t[t[v].fail].suffixes + 1;
            t[v].end = (int)s.size() - 2;
            t[u].next[c] = v;
        }
        last = t[u].next[c];
        t[last].hits++;
        total += t[last].suffixes;
        return last;
    }

    int Distinct() const
    {
        return tot - 1;
    }

    // Copy-and-propagate: repeated calls and later appends remain valid.
    vector<long long> Occurrences() const
    {
        vector<long long> count(tot + 1);
        for ( int u = 2; u <= tot; u++ )
            count[u] = t[u].hits;
        for ( int u = tot; u >= 2; u-- )
            count[t[u].fail] += count[u];
        count[0] = 0;
        count[1] = 0;
        return count;
    }
};
