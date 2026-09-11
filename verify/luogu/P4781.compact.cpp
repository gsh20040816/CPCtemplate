#include "../../src/compact/interpolation.hpp"
#include <iostream>

int main()
{
    std::ios::sync_with_stdio(false);
    std::cin.tie(nullptr);
    int n;
    long long k;
    std::cin >> n >> k;
    std::vector<long long> x(n), y(n);
    for (int i = 0; i < n; i++)
        std::cin >> x[i] >> y[i];
    Lagrange poly;
    poly.init(x, y, 998244353);
    std::cout << poly.query(k) << '\n';
}
