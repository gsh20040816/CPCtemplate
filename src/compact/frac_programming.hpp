#pragma once
#include <bits/stdc++.h>
using namespace std;

// BEGIN dinkelbach
// Maximize (sum a)/(sum b) over feasible choices with sum b > 0.
// best(lambda) returns {A, B} of a choice maximizing A - lambda * B; lambda starts at the
// ratio of any feasible choice. Lambda increases every round and stops at the optimum.
template <class F> double dinkelbach(F best, double lambda, double eps = 1e-10)
{
    while (true)
    {
        auto [A, B] = best(lambda);
        if (A - lambda * B <= eps * max(1.0, fabs(B))) return lambda;
        lambda = A / B;
    }
}
// END dinkelbach
