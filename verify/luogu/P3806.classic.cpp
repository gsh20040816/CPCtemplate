#include "../../src/classic/centroid.hpp"
#include <iostream>

int main()
{
    std::ios::sync_with_stdio(false);
    std::cin.tie(nullptr);
    int n, m;
    std::cin >> n >> m;
    static Centroid_Pairs<10000> tree;
    tree.Init(n);
    for ( int i = 1; i < n; i++ )
    {
        int u, v;
        long long w;
        std::cin >> u >> v >> w;
        tree.Insert(u, v, w);
    }
    tree.Build();
    while ( m-- )
    {
        long long k;
        std::cin >> k;
        std::cout << (tree.Count_Exact(k) ? "AYE" : "NAY") << '\n';
    }
}
