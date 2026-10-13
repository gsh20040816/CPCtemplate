#include <bits/stdc++.h>
using namespace std;
using i64 = long long;
#include "fixtures/wida_mcf7a/main.cpp"
#include "../src/compact/flow.hpp"

int main(int argc, char **argv)
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    string mode = argc > 1 ? argv[1] : "cases";
    if (mode == "overflow")
    {
        MCFGraph g(3);
        g.addEdge(0, 1, 1, 1);
        g.addEdge(0, 1, 1, 1);
        auto [f, c] = g.flow(1, 0);
        cout << f << ' ' << c << '\n';
        return 0;
    }
    MCFGraph direct(2);
    direct.addEdge(0, 1, 5, 3);
    auto [f0, c0] = direct.flow(0, 1);
    MCFGraph backward(2);
    backward.addEdge(0, 1, 5, 3);
    auto [f1, c1] = backward.flow(1, 0);
    MinCostFlow library(2);
    library.add(1, 2, 5, 3);
    auto lib = library.run(1, 2, LLONG_MAX, nullptr);
    cout << f0 << ' ' << c0 << '\n';
    cout << f1 << ' ' << c1 << '\n';
    cout << lib.first << ' ' << (long long)lib.second << '\n';
}
