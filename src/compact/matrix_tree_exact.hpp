#pragma once
#include "determinant_exact.hpp"
#include <tuple>
#include <utility>

template<class Z>
struct MatrixTreeExact
{
    using Edge = tuple<int, int, Z>;
    enum class Kind
    {
        undirected,
        toward_root,
        away_from_root
    };

    static Z count(int n, const vector<Edge> &edges, int root, Kind kind)
    {
        assert(n >= 1 && root >= 0 && root < n);
        vector<vector<Z>> lap(n - 1, vector<Z>(n - 1));
        auto add = [&](int u, int v, const Z &w)
        {
            if (u == root)
                return;
            int i = u - (u > root);
            int j = v - (v > root);
            lap[i][i] += w;
            if (v != root)
                lap[i][j] -= w;
        };
        for (auto [u, v, w] : edges)
        {
            assert(0 <= u && u < n && 0 <= v && v < n);
            if (u == v)
                continue;
            if (kind == Kind::away_from_root)
                swap(u, v);
            add(u, v, w);
            if (kind == Kind::undirected)
                add(v, u, w);
        }
        return determinant_exact(move(lap));
    }
};
