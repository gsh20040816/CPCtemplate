#include <bits/stdc++.h>
#include <cassert>
using i64 = long long;
#include "fixtures/wida_mint/main.cpp"

int main(int argc, char **argv)
{
    std::ios::sync_with_stdio(false);
    std::cin.tie(nullptr);
    std::string mode = argc > 1 ? argv[1] : "cases";
    if (mode == "inv0")
    {
        std::cout << Z(0).inv().val() << '\n';
        return 0;
    }
    if (mode == "overflow")
    {
        std::cout << mul(1000000000000000LL, 1000000000000000LL, 100000000000000003LL) << '\n';
        return 0;
    }
    constexpr int P = 1000000007;
    Z a(3), b(5);
    std::cout << (a + b).val() << ' ' << (a - b).val() << ' ' << (a * b).val() << ' ' << (a / b).val() << '\n';
    std::cout << power(Z(2), 10).val() << ' ' << (-a).val() << ' ' << Z(-5).val() << '\n';
    std::cout << MInt<0>::getMod() << '\n';
    MInt<0>::setMod(7);
    std::cout << MInt<0>(10).val() << '\n';
    int bad = 0;
    for (int i = 1; i <= 50; i++)
        for (int j = 1; j <= 50; j++)
        {
            i64 got = mul(i, j, 97);
            i64 expect = i64((__int128)i * j % 97);
            if (got != expect) bad++;
        }
    std::cout << bad << '\n';
}
