#pragma once
#include <algorithm>
#include <string>
#include <utility>
#include <vector>
#include "string.hpp"
using namespace std;

// BEGIN exkmp
// Return {Z(t), LCP(s[i..], t) for every i}; empty strings are allowed.
pair<vector<int>, vector<int>> exkmp(const string &s, const string &t)
{
    int n = s.size(), m = t.size();
    auto z = z_function(t);
    vector<int> p(n);
    for (int i = 0, l = 0, r = 0; i < n; i++)
    {
        if (i < r) p[i] = min(r - i, z[i - l]);
        while (p[i] < m && p[i] < n - i && s[i + p[i]] == t[p[i]])
            p[i]++;
        if (i + p[i] > r)
        {
            l = i;
            r = i + p[i];
        }
    }
    return {move(z), move(p)};
}
// END exkmp
