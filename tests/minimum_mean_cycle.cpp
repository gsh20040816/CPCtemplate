#include "../src/compact/minimum_mean_cycle.hpp"

#define CHECK(x) do { if (!(x)) { cerr << "line " << __LINE__ << '\n'; abort(); } } while (0)
using I = __int128_t;
using R = pair<I, int>;
using E = tuple<int, int, long long>;

optional<R> brute(int n, const vector<E> &edges)
{
    vector<vector<pair<int, long long>>> g(n);
    for (auto [u, v, w] : edges) g[u].emplace_back(v, w);
    optional<R> best;
    vector<bool> used(n);
    for (int start = 0; start < n; start++)
    {
        auto dfs = [&](auto &&self, int u, I sum, int len) -> void
        {
            used[u] = true;
            for (auto [v, w] : g[u])
            {
                if (v == start)
                {
                    R r{sum + w, len + 1};
                    if (!best || r.first * best->second < best->first * r.second)
                        best = r;
                }
                else if (v > start && !used[v]) self(self, v, sum + w, len + 1);
            }
            used[u] = false;
        };
        dfs(dfs, start, 0, 0);
    }
    return best;
}

void check(int n, const vector<E> &edges)
{
    auto want = brute(n, edges);
    auto got = minimum_mean_cycle(n, edges);
    CHECK(bool(want) == bool(got));
    if (want)
    {
        CHECK(1 <= got->second && got->second <= n);
        CHECK(want->first * got->second == got->first * want->second);
    }
    vector<tuple<int, int, long double>> real;
    bool small = true;
    for (auto [u, v, w] : edges)
    {
        real.emplace_back(u, v, (long double)w / 8);
        small &= (w >= -1000000 && w <= 1000000);
    }
    if (small)
    {
        auto r = minimum_mean_cycle(n, real);
        CHECK(bool(r) == bool(want));
        if (r)
        {
            long double a = r->first / r->second;
            long double b = (long double)want->first / want->second / 8;
            CHECK(fabsl(a - b) <= 1e-12L);
        }
    }
}

int main()
{
    check(0, {});
    for (int mask = 0; mask < 19683; mask++)
    {
        vector<E> e;
        int x = mask;
        for (int u = 0; u < 3; u++)
            for (int v = 0; v < 3; v++)
            {
                int digit = x % 3;
                x /= 3;
                if (digit) e.emplace_back(u, v, digit == 1 ? -3 : 7);
            }
        check(3, e);
    }
    for (int mask = 0; mask < 65536; mask++)
    {
        vector<E> e;
        for (int u = 0; u < 4; u++)
            for (int v = 0; v < 4; v++)
                if (mask >> (4 * u + v) & 1)
                    e.emplace_back(u, v, (u * 4 + v) * 3 % 7 - 3);
        check(4, e);
    }
    mt19937 rng(3199);
    for (int trial = 0; trial < 3000; trial++)
    {
        int n = rng() % 7 + 1;
        vector<E> e;
        for (int i = rng() % 20; i > 0; i--)
            e.emplace_back(rng() % n, rng() % n, (int)(rng() % 101) - 50);
        check(n, e);
        shuffle(e.begin(), e.end(), rng);
        check(n + 2, e);
    }
    check(3, {{0, 1, LLONG_MIN}, {1, 2, LLONG_MIN}, {2, 0, LLONG_MIN}});
    check(3, {{0, 1, LLONG_MAX}, {1, 2, LLONG_MAX}, {2, 0, LLONG_MAX}});
    check(4, {{0, 1, LLONG_MAX}, {1, 0, LLONG_MIN}, {2, 3, -2}, {3, 2, 1}});
    check(2, {{0, 1, LLONG_MIN}});
    int n = 3000;
    vector<E> e;
    for (int u = 0; u < n; u++) e.emplace_back(u, (u + 1) % n, 1);
    while (e.size() < 10000) e.emplace_back(rng() % n, rng() % n, rng() % 100 + 2);
    auto ans = minimum_mean_cycle(n, e);
    CHECK(ans && ans->first == ans->second);
    e.emplace_back(n / 2, n / 2, -1);
    ans = minimum_mean_cycle(n, e);
    CHECK(ans && ans->first == -ans->second);
    cout << "19683 ternary digraphs; 65536 weighted four-vertex digraphs; 3000 random multigraphs; full64 and 3000/10000 stress PASS\n";
}
