#include "../../src/classic/dynamic_kth.hpp"
#include <iostream>

struct Query
{
    char op;
    int x, y, k;
    long long value;
};

int main()
{
    std::ios::sync_with_stdio(false);
    std::cin.tie(nullptr);
    int n, m;
    std::cin >> n >> m;
    std::vector<long long> a(n), future;
    for ( auto &x : a )
        std::cin >> x;
    std::vector<Query> queries(m);
    for ( auto &q : queries )
    {
        std::cin >> q.op;
        if ( q.op == 'Q' )
            std::cin >> q.x >> q.y >> q.k;
        else
        {
            std::cin >> q.x >> q.value;
            future.push_back(q.value);
        }
    }
    static Dynamic_Kth<100000, 17000000> tree;
    tree.Init(a, future);
    for ( const auto &q : queries )
    {
        if ( q.op == 'Q' )
            std::cout << tree.Kth(q.x, q.y, q.k) << '\n';
        else
            tree.Set(q.x, q.value);
    }
}
