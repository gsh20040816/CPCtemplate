#include "../src/compact/biconnected.hpp"
#include <iostream>

int main()
{
    Biconnected g(4);
    g.add(1, 2);
    g.add(1, 2);
    g.add(2, 3);
    g.add(3, 3);
    g.run();
    assert(g.cnt == 3 && g.blocks.size() == 3);
    assert(g.cut[2] && !g.cut[1] && !g.cut[3] && !g.cut[4]);
    assert(g.bridge == vector<int>({0, 0, 1, 0}));
    assert(g.bel[1] == g.bel[2] && g.bel[2] != g.bel[3]);
    assert(g.block_forest() == block_cut_forest(g));
    assert(g.bridge_forest() == bridge_component_forest(g));
    g.add(3, 1);
    g.run();
    assert(g.cnt == 2 && g.blocks.size() == 2 && !g.cut[2]);
    assert(count(g.bridge.begin(), g.bridge.end(), 1) == 0);
    Biconnected empty(0);
    empty.run();
    assert(empty.block_forest().size() == 1 && empty.bridge_forest().size() == 1);
    cout << "Biconnected compatibility: parallel edges, bridge, loop, isolated vertex, repeated run and empty forests PASS\n";
}
