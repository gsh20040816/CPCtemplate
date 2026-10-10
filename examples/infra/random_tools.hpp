#include <bits/stdc++.h>
#include <cassert>
using namespace std;

mt19937_64 rng(712367821);

long long random_int(long long l, long long r) {
    return uniform_int_distribution<long long>(l, r)(rng);
}

double random_real(double l, double r) {
    return uniform_real_distribution<double>(l, r)(rng);
}

vector<int> permutation(int n) {
    vector<int> p(n);
    iota(p.begin(), p.end(), 0);
    shuffle(p.begin(), p.end(), rng);
    return p;
}

// Choose k distinct values from [0, n), using O(n) space.
vector<int> distinct_values(int n, int k) {
    assert(0 <= k && k <= n);
    auto p = permutation(n);
    p.resize(k);
    return p;
}

string random_string(int n, const string& alphabet) {
    assert(!alphabet.empty());
    string s(n, ' ');
    for (char& c : s) {
        c = alphabet[random_int(0, (int)alphabet.size() - 1)];
    }
    return s;
}

// Random recursive tree, then relabel; not uniform over all trees.
vector<pair<int, int>> random_tree(int n) {
    auto p = permutation(n);
    vector<pair<int, int>> edges;
    for (int i = 1; i < n; i++) {
        edges.emplace_back(p[i], p[random_int(0, i - 1)]);
    }
    shuffle(edges.begin(), edges.end(), rng);
    return edges;
}

// Small undirected simple graphs; O(n^2) time and space.
vector<pair<int, int>> random_graph(int n, int m) {
    assert(0 <= m && m <= 1LL * n * (n - 1) / 2);
    vector<pair<int, int>> edges;
    for (int u = 0; u < n; u++) {
        for (int v = u + 1; v < n; v++) {
            edges.emplace_back(u, v);
        }
    }
    shuffle(edges.begin(), edges.end(), rng);
    edges.resize(m);
    return edges;
}
