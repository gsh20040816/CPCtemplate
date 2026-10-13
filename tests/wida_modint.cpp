#include <bits/stdc++.h>
using u32 = std::uint32_t;
using u64 = std::uint64_t;
#include "fixtures/wida_modint/main.cpp"

int main(int argc, char **argv)
{
    std::ios::sync_with_stdio(false);
    std::cin.tie(nullptr);
    std::string mode = argc > 1 ? argv[1] : "mod";
    if (mode == "mul64")
    {
        constexpr u64 P = 11257775608867173391ULL;
        constexpr u64 A = 7454363357621997443ULL;
        constexpr u64 B = 342088715882458571ULL;
        u64 got = mulMod<P>(A, B);
        u64 expect = (u64)((__uint128_t)A * B % P);
        std::cout << got << ' ' << expect << '\n';
        return 0;
    }
    Z a(3), b(5), neg(-1), wide((long long)-5);
    std::cout << (a + b).val() << ' ' << (a - b).val() << ' ' << (a * b).val() << ' ' << (a / b).val() << '\n';
    std::cout << power(Z(2), 10).val() << ' ' << (-a).val() << ' ' << neg.val() << ' ' << wide.val() << '\n';
    std::cout << Z(0).inv().val() << ' ' << (a == Z(3)) << ' ' << (a < b) << '\n';
}
