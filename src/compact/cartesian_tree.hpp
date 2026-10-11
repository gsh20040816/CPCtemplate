#pragma once
#include <bits/stdc++.h>
using namespace std;

// BEGIN CartesianTree
struct CartesianTree
{
    int root;
    vector<int> left, right;
};

template <class T>
CartesianTree cartesian_tree(const vector<T> &a)
{
    int n = a.size();
    CartesianTree tree{-1, vector<int>(n, -1), vector<int>(n, -1)};
    vector<int> st;
    st.reserve(n);
    for (int i = 0; i < n; i++)
    {
        int last = -1;
        while (!st.empty() && a[i] < a[st.back()])
        {
            last = st.back();
            st.pop_back();
        }
        tree.left[i] = last;
        if (!st.empty()) tree.right[st.back()] = i;
        st.push_back(i);
    }
    if (n) tree.root = st.front();
    return tree;
}
// END CartesianTree
