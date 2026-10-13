#include <bits/stdc++.h>
#include <cassert>
using std::abs;
using std::__gcd;
#define MOD 1000000007
#include "fixtures/wida_overload/main.cpp"

int main(int argc, char **argv)
{
    std::string mode = argc > 1 ? argv[1] : "ok";
    if (mode == "pow") {
        std::cout << mypow(100000, 2, 1000000007) << '\n';
        return 0;
    }
    if (mode == "zero") {
        std::cout << Log2(0) << '\n';
        return 0;
    }
    if (mypow(2, 10) != 1024 || mypow(2, 10, 1000) != 24) return 1;
    if (mylcm(4, 6) != 12 || mylcm(0, 5) != 0) return 1;
    if (Log2(1) != 0 || Log2(2) != 1 || Log2(3) != 1 || Log2(8) != 3 || Log2(-1) != 31) return 1;
    if (ceiledLog2(1) != 0 || ceiledLog2(3) != 2 || ceiledLog2(5) != 3) return 1;
    if (floor(5, 2) != 2 || floor(-5, 2) != -3 || ceil(5, 2) != 3 || ceil(-5, 2) != -2) return 1;
    std::cout << "ok\n";
}
