#include "../../src/compact/tree_isomorphism.hpp"
#include <chrono>
#include <cstdio>
#include <random>

int main()
{
    int n;
    scanf("%d", &n);
    vector<vector<int>> g(n);
    for (int i = 1; i < n; i++)
    {
        int a, b;
        scanf("%d%d", &a, &b);
        a--, b--;
        g[a].push_back(b), g[b].push_back(a);
    }
    mt19937_64 rng(chrono::steady_clock::now().time_since_epoch().count());
    unsigned long long s1 = rng() | 1, s2 = rng() | 1;
    auto h = tree_hash(g, 0, s1, s2);
    sort(h.begin(), h.end());
    printf("%d\n", int(unique(h.begin(), h.end()) - h.begin()));
}
