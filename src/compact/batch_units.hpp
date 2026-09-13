#pragma once
#include <bits/stdc++.h>
using namespace std;

// BEGIN batch_units
template <class Z> optional<vector<Z>> batch_units(vector<Z> a)
{
    int n = a.size();
    vector<Z> pre(n + 1, Z(1));
    for (int i = 0; i < n; i++) pre[i + 1] = pre[i] * a[i];
    auto x = pre[n].try_inv();
    if (!x) return nullopt;
    Z inv = *x;
    for (int i = n - 1; i >= 0; i--)
    {
        Z old = a[i];
        a[i] = inv * pre[i];
        inv *= old;
    }
    return a;
}

// END batch_units
