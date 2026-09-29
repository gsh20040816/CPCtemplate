#include "../src/compact/flow.hpp"

int main()
{
    BoundedCirculation a(4);
    assert(!a.solved && !a.feasible);
    assert(a.add(1, 2, 2, 7) == 0);
    assert(a.add(1, 2, 3, 5) == 1);
    assert(a.add(2, 1, 5, 5) == 2);
    assert(a.add(3, 3, 9, 10) == 3);
    assert(a.add(4, 4, 0, 0) == 4);
    assert(a.ids == vector<int>({0, 2, 4, 6, 8}));
    assert(a.solve() && a.solved && a.feasible);
    assert(a.used(0) == 2 && a.used(1) == 3 && a.used(2) == 5);
    assert(a.used(3) == 9 && a.used(4) == 0);
    // Restored flow contains the lower bound, unlike residual-network used().
    assert(a.g.used(a.ids[0]) == 0 && a.used(0) == 2);

    BoundedCirculation b(3);
    b.add(1, 2, 1, 1);
    b.add(2, 1, 0, 1);
    b.add(2, 3, 1, 1);
    assert(!b.solve() && b.solved && !b.feasible);

    BoundedCirculation c(200);
    assert(c.solve() && c.lower.empty() && c.ids.empty());
    long long cap = 3000000000000000000LL;
    BoundedCirculation d(3);
    d.add(1, 2, cap, cap);
    d.add(2, 3, 0, cap);
    d.add(3, 1, 0, cap);
    assert(d.solve());
    for (int i = 0; i < 3; i++) assert(d.used(i) == cap);
    cout << "Circulation: original/residual IDs, lower-bound restoration, independent components, self-loops, empty edges, flags and int64 capacity PASS\n";
}
