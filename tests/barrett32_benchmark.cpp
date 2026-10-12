#include <bits/stdc++.h>
#include <cassert>
#include "../src/compact/dynamic_modint.hpp"
namespace before
{
#include "mint-before.hpp"
}
using namespace std;

template<class Z>
__attribute__((noinline)) int run(int mod, int count)
{
    Z::set_mod(mod);
    Z x(17), b(1234567), one(1);
    for (int i = 0; i < count; i++)
    {
        x *= b;
        x += one;
    }
    return x.v;
}

int main(int argc, char **argv)
{
    int mod = stoi(argv[1]);
    int count = stoi(argv[2]);
    auto start = chrono::steady_clock::now();
    int answer;
    if (string(argv[3]) == "before")
        answer = run<before::mint<>>(mod, count);
    else
        answer = run<mint<>>(mod, count);
    double elapsed = chrono::duration<double>(chrono::steady_clock::now() - start).count();
    cout << answer << ' ' << elapsed << '\n';
}
