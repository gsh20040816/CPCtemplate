#include "../src/compact/centroid_nearest.hpp"
#include <iostream>
#include <numeric>
#include <pthread.h>
#include <queue>
#include <random>
#include <stdexcept>

using ll = long long;
long long cases = 0, checks = 0;
std::mt19937 rng(29392026);

void require(bool ok)
{
    ++checks;
    if (!ok) throw std::runtime_error("oracle mismatch");
}

void check_tree(CentroidNearest tree, bool exhaustive)
{
    ++cases;
    int n = tree.n;
    // BFS over the original tree, with wide path sums: independent of centroids.
    std::vector<std::vector<ll>> d(n, std::vector<ll>(n));
    for (int s = 0; s < n; s++)
    {
        std::queue<int> q;
        std::vector<int> seen(n);
        q.push(s);
        seen[s] = 1;
        while (!q.empty())
        {
            int u = q.front();
            q.pop();
            for (auto [v, w] : tree.g[u])
            {
                if (seen[v]) continue;
                __int128 sum = (__int128)d[s][u] + w;
                require(sum <= LLONG_MAX);
                d[s][v] = (ll)sum;
                seen[v] = 1;
                q.push(v);
            }
        }
    }
    auto fresh = tree;
    fresh.build();
    tree.build();
    std::vector<int> on(n);
    auto verify = [&](const CentroidNearest &a)
    {
        for (int u = 0; u < n; u++)
        {
            std::optional<std::pair<ll, int>> want;
            for (int v = 0; v < n; v++)
            {
                if (!on[v]) continue;
                std::pair<ll, int> candidate{d[u][v], v};
                if (!want || candidate < *want) want = candidate;
            }
            require(a.query(u) == want);
            require(a.active[u] == on[u]);
        }
    };
    verify(tree);
    verify(fresh);
    int steps = exhaustive ? 1 << n : 200;
    for (int step = 0; step < steps; step++)
    {
        if (exhaustive)
        {
            int mask = step ^ (step >> 1);
            for (int u = 0; u < n; u++)
            {
                on[u] = mask >> u & 1;
                tree.set(u, on[u]);
                tree.set(u, on[u]);
            }
        }
        else
        {
            int u = rng() % n;
            on[u] ^= 1;
            tree.set(u, on[u]);
            tree.set(u, on[u]);
        }
        verify(tree);
        if (step % 17 == 0)
        {
            auto copy = tree;
            verify(copy);
            copy.set(0, !on[0]);
            verify(tree);
        }
    }
    tree.build();
    std::fill(on.begin(), on.end(), 0);
    verify(tree);
    for (int u = 0; u < n; u++) tree.set(u, true);
    for (int u = n - 1; u >= 0; u--) tree.set(u, false);
    verify(tree);
}

void small()
{
    check_tree(CentroidNearest(1), true);
    // Every labelled tree on up to 6 vertices, by Pruefer code.
    for (int n = 2; n <= 6; n++)
    {
        int count = 1;
        for (int i = 0; i < n - 2; i++) count *= n;
        for (int code = 0; code < count; code++)
        {
            std::vector<int> sequence(n - 2), degree(n, 1);
            int x = code;
            for (int &v : sequence)
            {
                v = x % n;
                x /= n;
                degree[v]++;
            }
            std::vector<std::pair<int, int>> edges;
            for (int v : sequence)
            {
                int u = 0;
                while (degree[u] != 1) u++;
                edges.push_back({u, v});
                degree[u]--;
                degree[v]--;
            }
            int u = 0, v = n - 1;
            while (degree[u] != 1) u++;
            while (degree[v] != 1) v--;
            edges.push_back({u, v});
            for (int kind = 0; kind < 3; kind++)
            {
                CentroidNearest tree(n);
                for (auto [a, b] : edges)
                    tree.add(a, b, kind == 0 ? 1 : kind == 1 ? 0 : (a * 7 + b) % 4);
                check_tree(tree, true);
            }
        }
    }
    for (int repeat = 0; repeat < 250; repeat++)
    {
        int n = 1 + rng() % 45;
        CentroidNearest tree(n);
        for (int v = 1; v < n; v++)
            tree.add(rng() % v, v, rng() % 8 == 0 ? 0 : rng() % 1000000000000LL);
        check_tree(tree, false);
    }
    CentroidNearest edge(2);
    edge.add(0, 1, LLONG_MAX);
    check_tree(edge, true);
    // Root centroid is 1. The centroid detour for query(0), active(0),
    // is 2*LLONG_MAX; the actual distance is zero.
    CentroidNearest detour(3);
    detour.add(0, 1, LLONG_MAX);
    detour.add(1, 2, 0);
    check_tree(detour, true);
}

void large()
{
    const int n = 100000;
    for (int shape = 0; shape < 3; shape++)
    {
        ++cases;
        CentroidNearest tree(n);
        for (int v = 1; v < n; v++)
            tree.add(shape == 0 ? v - 1 : shape == 1 ? 0 : (v - 1) / 2, v);
        tree.build();
        for (int u = 0; u < n; u++) require(!tree.query(u));
        for (int u = 0; u < n; u++) tree.set(u, true);
        for (int u = 0; u < n; u++)
            require(tree.query(u) == std::make_optional(std::make_pair(0LL, u)));
        for (int u = 0; u < n; u++) tree.set(u, false);
        tree.set(0, true);
        for (int u = 0; u < n; u++)
        {
            ll d = shape == 0 ? u : shape == 1 ? (u != 0) : 0;
            if (shape == 2)
                for (int v = u; v; v = (v - 1) / 2) d++;
            require(tree.query(u) == std::make_optional(std::make_pair(d, 0)));
        }
        tree.build();
        for (int u = 0; u < n; u++) require(!tree.query(u));
    }
}

void *worker(void *)
{
    try
    {
        small();
        large();
        std::cout << "PASS " << cases << " cases " << checks << " checks\n";
    }
    catch (const std::runtime_error &)
    {
        std::cout << "ORACLE_REJECT\n";
    }
    return nullptr;
}

int main()
{
    pthread_attr_t attr;
    if (pthread_attr_init(&attr)) return 2;
    if (pthread_attr_setstacksize(&attr, 256ULL << 20)) return 2;
    pthread_t thread;
    if (pthread_create(&thread, &attr, worker, nullptr)) return 2;
    if (pthread_attr_destroy(&attr)) return 2;
    if (pthread_join(thread, nullptr)) return 2;
}
