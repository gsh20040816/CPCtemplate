#include <bits/stdc++.h>
#include <cassert>
using namespace std;
#include "fixtures/wida_modclass/main.cpp"

int main(int argc, char **argv)
{
    string mode = argc > 1 ? argv[1] : "ok";
    if (mode == "inv") {
        cout << Z(0).inv().val() << '\n';
        return 0;
    }
    if (mode == "mod0") {
        cout << (Z(10) % 0).val() << '\n';
        return 0;
    }
    constexpr int P = 998244353;
    Z a(3), b(5);
    if ((a + b).val() != 8 || (a - b).val() != (3 - 5 + P) % P) return 1;
    if ((a * b).val() != 15 || (a / b * b).val() != 3) return 1;
    if (Z(-1).val() != P - 1 || (-a).val() != P - 3) return 1;
    Z c(P - 1);
    ++c;
    if (c.val() != 0) return 1;
    --c;
    if (c.val() != P - 1) return 1;
    if (power(10).val() != 1024 || (Z(10) % 4).val() != 2) return 1;
    cout << "ok\n";
}
