#include "../../src/classic/tree_path_kth.hpp"
#include <iostream>

int main()
{
    std::ios::sync_with_stdio(false);
    std::cin.tie(nullptr);
    int n, m;
    std::cin >> n >> m;
    std::vector<long long> a(n);
    for ( auto &x : a )
        std::cin >> x;
    static Tree_Path_Kth<100000, 2000000, 17> tree;
    tree.Init(a);
    for ( int i = 1; i < n; i++ )
    {
        int u, v;
        std::cin >> u >> v;
        tree.Insert(u, v);
    }
    tree.Build();
    long long last = 0;
    while ( m-- )
    {
        long long encoded;
        int v, k;
        std::cin >> encoded >> v >> k;
        int u = encoded ^ last;
        last = tree.Kth(u, v, k);
        std::cout << last << '\n';
    }
}
