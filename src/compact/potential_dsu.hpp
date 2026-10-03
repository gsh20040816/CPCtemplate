#pragma once
#include <cassert>
#include <numeric>
#include <optional>
#include <utility>
#include <vector>
using namespace std;

// BEGIN PotentialDSU
template <class T = long long> struct PotentialDSU
{
    vector<int> fa, sz;
    vector<T> d;

    PotentialDSU(int n) : fa(n), sz(n, 1), d(n, T(0))
    {
        iota(fa.begin(), fa.end(), 0);
    }

    int find(int u)
    {
        assert(0 <= u && u < (int)fa.size());
        int p = fa[u];
        if (p != u)
        {
            fa[u] = find(p);
            d[u] = d[u] + d[p];
        }
        return fa[u];
    }

    // Accept potential[u] - potential[v] = w iff it is consistent.
    bool merge(int u, int v, T w)
    {
        int a = find(u), b = find(v);
        if (a == b) return d[u] - d[v] == w;
        T t = d[u] - d[v] - w;
        if (sz[a] < sz[b])
        {
            swap(a, b);
            t = T(0) - t;
        }
        fa[b] = a;
        d[b] = t;
        sz[a] += sz[b];
        return true;
    }

    optional<T> diff(int u, int v)
    {
        int a = find(u), b = find(v);
        if (a != b) return nullopt;
        return d[u] - d[v];
    }

    int size(int u) { return sz[find(u)]; }
};

// END PotentialDSU
