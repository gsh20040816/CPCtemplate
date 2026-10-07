#include <bits/stdc++.h>
#include <boost/multiprecision/cpp_int.hpp>
#include "../../src/compact/matrix_tree_exact.hpp"
using namespace std;

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    using Z = boost::multiprecision::cpp_int;
    using Tree = MatrixTreeExact<Z>;
    int t;
    cin >> t;
    while (t--)
    {
        int n, m, root, type;
        cin >> n >> m >> root >> type;
        vector<Tree::Edge> edges(m);
        for (auto &[u, v, w] : edges)
            cin >> u >> v >> w;
        auto kind = Tree::Kind::undirected;
        if (type == 1)
            kind = Tree::Kind::toward_root;
        if (type == 2)
            kind = Tree::Kind::away_from_root;
        cout << Tree::count(n, edges, root, kind) << '\n';
    }
    return 0;
}
