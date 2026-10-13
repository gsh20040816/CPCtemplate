#include <bits/stdc++.h>
#include <cassert>
#include "fixtures/wida_z/main.cpp"

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
    i64 neg = -1;
    i64 wide = (i64)-P - 1;
    std::cout << Z(-1).val() << ' ' << Z(neg).val() << '\n';
    std::cout << Z(-P).val() << ' ' << Z(wide).val() << ' ' << Z(-P - 1).val() << '\n';
    Z a(3), b(5);
    std::cout << (a + b).val() << ' ' << (a - b).val() << ' ' << (a * b).val() << ' ' << (a / b).val() << '\n';
    std::cout << power(Z(2), 10).val() << ' ' << (-a).val() << '\n';
    Z in;
    std::cin >> in;
    std::cout << in.val() << '\n';
}
