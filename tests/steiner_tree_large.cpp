#include "../src/compact/steiner_tree.hpp"

int main()
{
    for (int mode = 0; mode < 3; mode++)
    {
        SteinerTree s(100);
        for (int v = 1; v < 100; v++)
            s.add(mode == 0 ? v - 1 : 0, v, mode == 2 ? 0 : 1);
        mt19937 rng(17);
        while (s.edges.size() < 500)
            s.add(rng() % 100, rng() % 100, 1000000);
        vector<int> terminals;
        for (int i = 0; i < 10; i++) terminals.push_back(i * 11);
        auto begin = chrono::steady_clock::now();
        auto result = s.solve(terminals);
        long long expected = mode == 0 ? 99 : mode == 1 ? 9 : 0;
        if (result.cost != expected) abort();
        long long sum = 0;
        for (int id : result.edges) sum += s.edges[id].w;
        if (sum != expected) abort();
        cout << mode << ' ' << result.cost << ' '
             << chrono::duration<double>(chrono::steady_clock::now() - begin).count() << '\n';
    }
}
