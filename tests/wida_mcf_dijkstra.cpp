#include <bits/stdc++.h>
using namespace std;
#include "fixtures/wida_mcf_dijkstra/main.cpp"

int main(int argc, char **argv)
{
    string mode = argc > 1 ? argv[1] : "ok";
    if (mode == "island") {
        MinCostFlow g(3);
        g.add(0, 1, 1, 1);
        g.add(0, 1, 1, 1);
        auto [flow, cost] = g.flow(0, 1);
        cout << flow << ' ' << cost << '\n';
        return 0;
    }
    MinCostFlow g(4);
    g.add(0, 1, 2, 1);
    g.add(0, 2, 1, 2);
    g.add(1, 3, 1, 3);
    g.add(2, 3, 2, 1);
    auto [flow, cost] = g.flow(0, 3);
    MinCostFlow p(2);
    p.add(0, 1, 1, 4);
    p.add(0, 1, 1, 1);
    auto [pf, pc] = p.flow(0, 1);
    MinCostFlow neg(2);
    neg.add(0, 1, 1, -5);
    auto [nf, nc] = neg.flow(0, 1);
    cout << flow << ' ' << cost << '\n' << pf << ' ' << pc << '\n' << nf << ' ' << nc << '\n';
}
