#pragma once
#include <cassert>
#include <string>
#include <vector>
#include "data_structure.hpp"
using namespace std;

// Build from the same documents as sam; keep sam alive and unchanged.
template <class S>
struct SAMDocuments
{
    const S &sam;
    vector<vector<int>> g;
    vector<int> cnt;

    SAMDocuments(const S &sam, const vector<string> &s)
        : sam(sam), g(sam.a.size()), cnt(sam.a.size())
    {
        int n = sam.a.size(), size = 0;
        vector<vector<int>> tag(n);
        for (int u = 1; u < n; u++) g[sam.a[u].link].push_back(u);
        for (int id = 0; id < (int)s.size(); id++)
        {
            int p = 0, len = 0;
            for (char c : s[id])
            {
                assert('a' <= c && c <= 'z');
                p = sam.a[p].go[c - 'a'];
                len++;
                assert(p && sam.a[p].len == len);
                tag[p].push_back(id);
                size++;
            }
        }
        Fenwick<int> bit(size);
        vector<int> last(s.size());
        int timer = 0;
        auto dfs = [&](auto &&self, int u) -> void
        {
            int l = timer + 1;
            for (int id : tag[u])
            {
                if (last[id]) bit.add(last[id], -1);
                last[id] = ++timer;
                bit.add(timer, 1);
            }
            for (int v : g[u]) self(self, v);
            cnt[u] = bit.query(l, timer);
        };
        dfs(dfs, 0);
        cnt[0] = s.size();
    }

    // Longest suffix length occurring in at least k documents, for each state.
    vector<int> lengths(int k) const
    {
        assert(k >= 1);
        vector<int> best(cnt.size());
        auto dfs = [&](auto &&self, int u) -> void
        {
            if (cnt[u] >= k) best[u] = sam.a[u].len;
            for (int v : g[u])
            {
                best[v] = best[u];
                self(self, v);
            }
        };
        dfs(dfs, 0);
        return best;
    }
};
