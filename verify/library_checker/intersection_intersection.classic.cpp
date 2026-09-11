// https://judge.yosupo.jp/problem/intersection_of_f2_vector_spaces
#include "../../src/classic/basis_intersection.hpp"
#include <iostream>

int main()
{
    std::ios::sync_with_stdio(false);
    std::cin.tie(nullptr);
    int tests;
    std::cin >> tests;
    while (tests--)
    {
        Xor_Basis a, b;
        int n, m;
        std::cin >> n;
        for (int i = 0; i < n; i++)
        {
            unsigned long long x;
            std::cin >> x;
            a.Insert(x);
        }
        std::cin >> m;
        for (int i = 0; i < m; i++)
        {
            unsigned long long x;
            std::cin >> x;
            b.Insert(x);
        }
        auto result = Basis_Intersection(a,b);
        std::cout << result.rank;
        for (auto x : result.base)
            if (x)
                std::cout << ' ' << x;
        std::cout << '\n';
    }
}
