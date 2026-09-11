#include "../../src/classic/position_basis.hpp"
#include <array>
#include <iostream>
#include <vector>

int main()
{
    std::ios::sync_with_stdio(false);
    std::cin.tie(nullptr);
    int n, q;
    std::cin >> n;
    std::vector<unsigned long long> a(n + 1);
    for ( int i = 1; i <= n; i++ )
        std::cin >> a[i];
    std::cin >> q;
    std::vector<std::array<int, 3>> queries(q);
    for ( int i = 0; i < q; i++ )
    {
        int l, r;
        std::cin >> l >> r;
        queries[i] = {r, l, i};
    }
    std::sort(queries.begin(), queries.end());
    std::vector<unsigned long long> answer(q);
    Position_Basis basis;
    int right = 0;
    for ( auto [r, l, id] : queries )
    {
        while ( right < r )
        {
            right++;
            basis.Insert(a[right], right);
        }
        answer[id] = basis.Query(l);
    }
    for ( auto x : answer )
        std::cout << x << '\n';
}
