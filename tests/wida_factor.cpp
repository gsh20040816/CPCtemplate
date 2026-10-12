#include <bits/stdc++.h>
#include <cassert>
using namespace std;
namespace source
{
using i64 = long long;
#include "fixtures/wida_factor/factor.cpp"
}
#include "../src/compact/number_theory.hpp"

int main()
{
    PollardRho solver;
    char task;
    unsigned long long n;
    while (cin >> task >> n)
    {
        if (task == 'p')
            cout << source::isprime(n) << ' ' << Prime64::prime(n);
        if (task == 'f')
        {
            auto old = source::factorize(n);
            cout << old.size();
            for (auto x : old)
                cout << ' ' << x;
            cout << " | ";
            auto now = solver.factor(n);
            cout << now.size();
            for (auto x : now)
                cout << ' ' << x;
        }
        if (task == 'u')
        {
            auto now = solver.factor(n);
            cout << now.size();
            for (auto x : now)
                cout << ' ' << x;
        }
        if (task == 'm' || task == 'w')
        {
            unsigned long long a, b;
            cin >> a >> b;
            if (task == 'm')
                cout << source::mul(a, b, n) << ' ' << Mod64::mul(a, b, n);
            else
                cout << source::power(a, b, n) << ' ' << Mod64::power(a, b, n);
        }
        cout << '\n';
    }
}
