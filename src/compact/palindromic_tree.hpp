#pragma once
#include <cassert>
#include <vector>
using namespace std;

struct PalindromicTree
{
    struct Node
    {
        int next[26]{};
        int len = 0, fail = 0, suffixes = 0, end = -1;
        long long hits = 0;
    };

    vector<Node> t;
    vector<int> s;
    int last = 0;
    long long total = 0;

    PalindromicTree() { init(); }

    void init()
    {
        t.assign(2, Node{});
        t[0].fail = 1;
        t[1].len = -1;
        s.assign(1, -1);
        last = 0;
        total = 0;
    }

    int get_fail(int u) const
    {
        int pos = s.size() - 1;
        while (s[pos - t[u].len - 1] != s[pos]) u = t[u].fail;
        return u;
    }

    // Append a lowercase letter; return the longest palindromic suffix node.
    int add(char ch)
    {
        int c = ch - 'a';
        assert(0 <= c && c < 26);
        s.push_back(c);
        int u = get_fail(last);
        if (!t[u].next[c])
        {
            int v = t.size();
            t.push_back(Node{});
            t[v].len = t[u].len + 2;
            t[v].fail = t[get_fail(t[u].fail)].next[c];
            t[v].suffixes = t[t[v].fail].suffixes + 1;
            t[v].end = (int)s.size() - 2;
            t[u].next[c] = v;
        }
        last = t[u].next[c];
        t[last].hits++;
        total += t[last].suffixes;
        return last;
    }

    int distinct() const { return (int)t.size() - 2; }

    // Copy-and-propagate: repeated calls and later appends remain valid.
    vector<long long> occurrences() const
    {
        vector<long long> count(t.size());
        for (int u = 2; u < (int)t.size(); u++) count[u] = t[u].hits;
        for (int u = (int)t.size() - 1; u >= 2; u--) count[t[u].fail] += count[u];
        count[0] = 0;
        count[1] = 0;
        return count;
    }
};
