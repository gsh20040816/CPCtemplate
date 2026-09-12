#pragma once
#include "algebra.hpp"

template <int mod> struct MatrixTree
{
    using A = LinearAlgebra<mod>;
    using Z = typename A::Z;
    using Edge = tuple<int, int, Z>;
    enum class Kind
    {
        undirected,
        toward_root,
        away_from_root
    };

    // Sum of products of edge weights; vertices 0..n-1, prime modulus.
    static Z count(int n, const vector<Edge> &edges, int root, Kind kind)
    {
        assert(n >= 1 && root >= 0 && root < n);
        typename A::Matrix lap(n - 1, vector<Z>(n - 1));
        auto add = [&](int u, int v, Z w)
        {
            if (u == root)
                return;
            int i = u - (u > root), j = v - (v > root);
            lap[i][i] = lap[i][i] + w;
            if (v != root)
                lap[i][j] = lap[i][j] - w;
        };
        for (auto [u, v, w] : edges)
        {
            assert(u >= 0 && u < n && v >= 0 && v < n);
            if (u == v)
                continue;
            if (kind == Kind::away_from_root)
                swap(u, v);
            add(u, v, w);
            if (kind == Kind::undirected)
                add(v, u, w);
        }
        return A::determinant(lap);
    }
};
