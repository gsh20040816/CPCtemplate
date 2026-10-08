#include "../src/compact/time_connectivity.hpp"

void need(bool ok)
{
    if (!ok)
        exit(1);
}

int main()
{
    mt19937 rng(2147352);
    for (int test = 0; test < 4000; ++test)
    {
        int n = rng() % 9;
        int q = rng() % 23;
        TimeConnectivity g(n, q);
        vector<array<int, 4>> intervals;
        for (int i = 0; i < 50; ++i)
        {
            int l = rng() % (q + 1);
            int r = rng() % (q + 1);
            if (l > r)
                swap(l, r);
            int u = rng() % (n + 1);
            int v = rng() % (n + 1);
            g.add(l, r, u, v);
            intervals.push_back({l, r, u, v});
        }
        auto check = [&]()
        {
            int calls = 0;
            g.run([&](int t, const RollbackDSU &d)
            {
                need(t == calls++);
                vector<vector<int>> a(n + 1);
                for (auto [l, r, u, v] : intervals)
                    if (l <= t && t < r)
                    {
                        a[u].push_back(v);
                        a[v].push_back(u);
                    }
                for (int u = 0; u <= n; ++u)
                {
                    vector<int> seen(n + 1);
                    queue<int> todo;
                    todo.push(u);
                    seen[u] = 1;
                    int size = 0;
                    while (!todo.empty())
                    {
                        int x = todo.front();
                        todo.pop();
                        ++size;
                        for (int v : a[x])
                            if (!seen[v])
                            {
                                seen[v] = 1;
                                todo.push(v);
                            }
                    }
                    need(size == d.siz[d.find(u)]);
                    for (int v = 0; v <= n; ++v)
                        need(bool(seen[v]) == (d.find(u) == d.find(v)));
                }
            });
            need(calls == q);
        };
        check();
        check();
        g.add(0, q, 0, n);
        intervals.push_back({0, q, 0, n});
        check();
    }
    cout << "4000 interval graphs; repeated run and add-after-run PASS\n";
}
