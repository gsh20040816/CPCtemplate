#pragma once
#include <algorithm>
#include <bit>
#include <cassert>
#include <cmath>
#include <numeric>
#include <utility>
#include <vector>
using namespace std;

// BEGIN xor_hamming_pairs
// Queries are 0-based half-open; count unordered pairs of distinct indices.
vector<long long> xor_hamming_pairs(const vector<int> &a,
                                    const vector<pair<int, int>> &queries,
                                    int k,
                                    int bits = 14)
{
    int n = a.size(), m = queries.size();
    vector<long long> answer(m);
    assert(0 <= bits && bits <= 20);
    int universe = 1 << bits;
    for (int x : a) assert(0 <= x && x < universe);
    for (auto [l, r] : queries) assert(0 <= l && l <= r && r <= n);
    if (!m || k < 0 || k > bits) return answer;
    vector<int> masks;
    for (int x = 0; x < universe; x++)
        if (popcount(unsigned(x)) == k) masks.push_back(x);
    vector<int> count(universe);
    vector<long long> prefix(n + 1);
    for (int i = 0; i < n; i++)
    {
        prefix[i + 1] = prefix[i] + count[a[i]];
        for (int mask : masks) count[a[i] ^ mask]++;
    }
    int block = max(1, int(n / sqrt(m)));
    vector<int> order(m);
    iota(order.begin(), order.end(), 0);
    sort(order.begin(),
         order.end(),
         [&](int x, int y)
         {
             int bx = queries[x].first / block, by = queries[y].first / block;
             if (bx != by) return bx < by;
             return bx & 1 ? queries[x].second > queries[y].second
                           : queries[x].second < queries[y].second;
         });

    struct Event
    {
        int id, l, r, sign;
    };

    vector<vector<Event>> events(n + 1);
    int l = 0, r = 0;
    for (int id : order)
    {
        auto [ql, qr] = queries[id];
        if (r < qr)
        {
            events[l].push_back({id, r, qr, -1});
            answer[id] += prefix[qr] - prefix[r];
            r = qr;
        }
        if (l > ql)
        {
            events[r].push_back({id, ql, l, 1});
            answer[id] -= prefix[l] - prefix[ql];
            l = ql;
        }
        if (r > qr)
        {
            events[l].push_back({id, qr, r, 1});
            answer[id] -= prefix[r] - prefix[qr];
            r = qr;
        }
        if (l < ql)
        {
            events[r].push_back({id, l, ql, -1});
            answer[id] += prefix[ql] - prefix[l];
            l = ql;
        }
    }
    fill(count.begin(), count.end(), 0);
    for (int p = 0; p <= n; p++)
    {
        if (p)
            for (int mask : masks) count[a[p - 1] ^ mask]++;
        for (auto e : events[p])
            for (int i = e.l; i < e.r; i++)
            {
                int value = count[a[i]] - (k == 0 && i < p);
                answer[e.id] += 1LL * e.sign * value;
            }
    }
    long long total = 0;
    for (int id : order)
    {
        total += answer[id];
        answer[id] = total;
    }
    return answer;
}

// END xor_hamming_pairs
