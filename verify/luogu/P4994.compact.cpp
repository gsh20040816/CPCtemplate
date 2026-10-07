#include <bits/stdc++.h>
#include "../../src/compact/fibonacci_period.hpp"
using namespace std;

int main()
{
    unsigned long long m;
    cin >> m;
    FibonacciPeriod solver;
    cout << (unsigned long long)solver.period(m) << '\n';
    return 0;
}
