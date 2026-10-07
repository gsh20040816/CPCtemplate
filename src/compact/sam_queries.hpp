#pragma once
#include <algorithm>
#include <cassert>
#include <climits>
#include <optional>
#include <string>
#include <utility>
#include <vector>
using namespace std;

// BEGIN SAMLex
// Keep sam alive and unchanged while this index is used.
template <class S>
struct SAMLex
{
    const S &sam;
    vector<long long> weight, sum;

    SAMLex(const S &sam, vector<long long> w = {}) : sam(sam), weight(move(w))
    {
        int n = sam.a.size(), length = 0;
        if (weight.empty()) weight.assign(n, 1);
        assert((int)weight.size() == n);
        weight[0] = 0;
        sum = weight;
        for (auto &v : sam.a) length = max(length, v.len);
        vector<int> bucket(length + 1), order(n);
        for (auto &v : sam.a) bucket[v.len]++;
        for (int i = 1; i <= length; i++) bucket[i] += bucket[i - 1];
        for (int i = 0; i < n; i++) order[--bucket[sam.a[i].len]] = i;
        for (int i = n - 1; i >= 0; i--)
        {
            int u = order[i];
            for (int v : sam.a[u].go)
                if (v) sum[u] += min(sum[v], LLONG_MAX - sum[u]);
        }
    }

    // alphabet must be a permutation of a..z; k is 1-based.
    optional<string> kth(long long k, const string &alphabet = "abcdefghijklmnopqrstuvwxyz") const
    {
        if (k <= 0 || k > sum[0]) return nullopt;
        int u = 0;
        string ans;
        while (k > weight[u])
        {
            k -= weight[u];
            for (char c : alphabet)
            {
                int v = sam.a[u].go[c - 'a'];
                if (!v) continue;
                if (k > sum[v]) k -= sum[v];
                else
                {
                    ans += c;
                    u = v;
                    break;
                }
            }
        }
        return ans;
    }
};
// END SAMLex

// BEGIN sam_lcs
// Return {start, length} in t; ties choose the earliest start.
template <class S>
pair<int, int> sam_lcs(const S &sam, const string &t)
{
    int p = 0, length = 0;
    pair<int, int> ans{0, 0};
    for (int i = 0; i < (int)t.size(); i++)
    {
        int c = t[i] - 'a';
        assert(0 <= c && c < 26);
        while (p && !sam.a[p].go[c])
        {
            p = sam.a[p].link;
            length = sam.a[p].len;
        }
        if (sam.a[p].go[c])
        {
            p = sam.a[p].go[c];
            length++;
        }
        else length = 0;
        if (length > ans.second) ans = {i - length + 1, length};
    }
    return ans;
}
// END sam_lcs
