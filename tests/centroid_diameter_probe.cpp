#include "../src/compact/centroid_diameter.hpp"
#include <cstdlib>
#include <iostream>
#include <numeric>
#include <queue>
#include <random>

using ll = long long;
long long cases = 0, checks = 0;

void require(bool ok)
{
    if (!ok)
    {
        cout << "ORACLE_REJECT\n";
        exit(0);
    }
}

vector<vector<ll>> distances(const CentroidDiameter &t)
{
    vector<vector<ll>> d(t.n, vector<ll>(t.n));
    for (int s = 0; s < t.n; s++)
    {
        vector<int> p(t.n, -1);
        queue<int> q;
        p[s] = s;
        q.push(s);
        while (!q.empty())
        {
            int u = q.front();
            q.pop();
            for (auto [v, w] : t.g[u])
            {
                if (p[v] != -1) continue;
                p[v] = u;
                __int128 x = (__int128)d[s][u] + w;
                require(LLONG_MIN <= x && x <= LLONG_MAX);
                d[s][v] = (ll)x;
                q.push(v);
            }
        }
    }
    return d;
}

void check(const CentroidDiameter &t, const vector<int> &on, const vector<vector<ll>> &d)
{
    ++checks;
    auto ans = t.query();
    int count = accumulate(on.begin(), on.end(), 0);
    require(bool(ans) == (count > 0));
    require(t.active == on && t.live.size() == (size_t)count);
    ll want = 0;
    for (int u = 0; u < t.n; u++)
        for (int v = 0; v < t.n; v++)
            if (on[u] && on[v]) want = max(want, d[u][v]);
    if (ans)
    {
        auto [x, u, v] = *ans;
        require(0 <= u && u < t.n && 0 <= v && v < t.n);
        require(on[u] && on[v] && x == want && d[u][v] == x);
    }
    size_t expected = 0, actual = 0;
    for (int u = 0; u < t.n; u++)
        if (on[u]) expected += t.path[u].size();
    for (const auto &b : t.bag) actual += b.size();
    require(expected == actual);
    require(t.bag.size() == (size_t)(2 * t.n - 1));
    require(t.best.size() <= (size_t)t.n);
}

void small(vector<tuple<int, int, ll>> edges)
{
    int n = edges.size() + 1;
    CentroidDiameter t(n);
    for (auto [u, v, w] : edges) t.add(u, v, w);
    t.build();
    auto d = distances(t);
    vector<int> on(n);
    check(t, on, d);
    int previous = 0;
    for (int mask = 1; mask < (1 << n); mask++)
    {
        int now = mask ^ (mask >> 1);
        int u = __builtin_ctz((unsigned)(now ^ previous));
        on[u] = now >> u & 1;
        t.set(u, on[u]);
        t.set(u, on[u]);
        check(t, on, d);
        previous = now;
    }
    auto copy = t;
    t.build();
    check(t, vector<int>(n), d);
    check(copy, on, d);
    for (int u = 0; u < n; u++) t.set(u, true);
    check(t, vector<int>(n, 1), d);
    ++cases;
}

void exhaustive()
{
    for (int n = 1; n <= 6; n++)
    {
        int count = 1;
        for (int i = 0; i < n - 2; i++) count *= n;
        for (int code = 0; code < count; code++)
        {
            int x = code;
            vector<int> seq(max(0, n - 2)), deg(n, 1);
            for (int &v : seq)
            {
                v = x % n;
                x /= n;
                ++deg[v];
            }
            vector<pair<int, int>> edges;
            for (int v : seq)
            {
                int u = find(deg.begin(), deg.end(), 1) - deg.begin();
                edges.push_back({u, v});
                --deg[u];
                --deg[v];
            }
            if (n > 1)
            {
                int u = find(deg.begin(), deg.end(), 1) - deg.begin();
                int v = find(deg.begin() + u + 1, deg.end(), 1) - deg.begin();
                edges.push_back({u, v});
            }
            int weights = 4;
            if (n <= 4)
            {
                weights = 1;
                for (int i = 1; i < n; i++) weights *= 3;
            }
            for (int pattern = 0; pattern < weights; pattern++)
            {
                vector<tuple<int, int, ll>> input;
                int y = pattern;
                for (auto [u, v] : edges)
                {
                    ll w = n <= 4 ? y % 3 - 1 : pattern == 0 ? 0 : pattern == 1 ? -1 : pattern == 2 ? 2 : (u + v) % 5 - 2;
                    y /= 3;
                    input.push_back({u, v, w});
                }
                small(input);
            }
        }
    }
    small({{0, 1, LLONG_MAX}, {0, 2, LLONG_MIN}});
    small({{0, 1, LLONG_MIN}, {1, 2, LLONG_MAX}});
    small({{0, 1, LLONG_MAX}});
    small({{0, 1, LLONG_MIN}});
    mt19937 rng(284);
    for (int test = 0; test < 100; test++)
    {
        int n = 2 + rng() % 25;
        CentroidDiameter t(n);
        for (int u = 1; u < n; u++) t.add(u, rng() % u, (int)(rng() % 101) - 50);
        t.build();
        auto d = distances(t);
        vector<int> on(n);
        for (int step = 0; step < 500; step++)
        {
            int u = rng() % n;
            on[u] = rng() % 2;
            t.set(u, on[u]);
            check(t, on, d);
        }
        ++cases;
    }
}

void large()
{
    int n = 100000;
    for (int shape = 0; shape < 3; shape++)
    {
        CentroidDiameter t(n);
        for (int u = 1; u < n; u++)
            t.add(shape == 2 ? 0 : u - 1, u, shape == 0 ? 1 : shape == 1 ? -1 : u % 2 ? 5 : -3);
        t.build();
        std::set<int> on;
        int positive = 0;
        auto verify = [&]()
        {
            ++checks;
            auto ans = t.query();
            require(bool(ans) == !on.empty());
            if (!ans) return;
            auto [d, u, v] = *ans;
            require(on.count(u) && on.count(v));
            ll actual = shape == 0 ? abs(u - v) : shape == 1 ? -abs(u - v) : u == v ? 0 : (u ? (u % 2 ? 5 : -3) : 0) + (v ? (v % 2 ? 5 : -3) : 0);
            ll want = shape == 0 ? *on.rbegin() - *on.begin() : shape == 1 ? 0 : positive >= 2 ? 10 : positive && on.count(0) ? 5 : positive && on.size() >= 2 ? 2 : 0;
            require(d == actual && d == want);
        };
        verify();
        for (int u = 0; u < n; u++)
        {
            t.set(u, true);
            on.insert(u);
            if (u % 2) ++positive;
            verify();
        }
        for (int i = 0; i < n; i++)
        {
            int u = (long long)i * 317 % n;
            t.set(u, false);
            on.erase(u);
            if (u % 2) --positive;
            verify();
        }
        for (const auto &b : t.bag) require(b.empty());
        require(t.best.empty());
        cout << "large " << shape << " PASS\n";
    }
}

int main(int argc, char **)
{
    exhaustive();
    cout << "small " << cases << " cases " << checks << " checks PASS\n";
    if (argc == 1) large();
    cout << "PASS " << cases << " cases " << checks << " checks\n";
}
