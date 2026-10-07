#pragma once
#include <cassert>
#include <iterator>
#include <map>
#include <vector>
using namespace std;

// BEGIN order_match
// Match all pairwise <, =, > relations; t must be nonempty.
vector<int> order_match(const vector<long long> &s, const vector<long long> &t)
{
    assert(!t.empty());
    int n = s.size(), m = t.size();
    vector<int> eq(m, -1), lo(m, -1), hi(m, -1), p(m), ans;
    map<long long, int> last;
    for (int j = 0; j < m; j++)
    {
        auto it = last.lower_bound(t[j]);
        if (it != last.end() && it->first == t[j])
            eq[j] = it->second;
        else
        {
            if (it != last.end()) hi[j] = it->second;
            if (it != last.begin()) lo[j] = prev(it)->second;
        }
        last[t[j]] = j;
    }
    auto fits = [&](const vector<long long> &a, int i, int j)
    {
        int start = i - j;
        if (eq[j] != -1) return a[i] == a[start + eq[j]];
        if (lo[j] != -1 && a[i] <= a[start + lo[j]]) return false;
        if (hi[j] != -1 && a[i] >= a[start + hi[j]]) return false;
        return true;
    };
    for (int i = 1, j = 0; i < m; i++)
    {
        while (j && !fits(t, i, j)) j = p[j - 1];
        if (fits(t, i, j)) j++;
        p[i] = j;
    }
    for (int i = 0, j = 0; i < n; i++)
    {
        while (j && !fits(s, i, j)) j = p[j - 1];
        if (fits(s, i, j)) j++;
        if (j == m)
        {
            ans.push_back(i - m + 1);
            j = p[j - 1];
        }
    }
    return ans;
}
// END order_match
