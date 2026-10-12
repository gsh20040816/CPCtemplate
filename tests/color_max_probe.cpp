#include "../src/compact/color_max.hpp"

long long states = 0;

void require(bool ok)
{
    if (!ok) throw runtime_error("ColorMax oracle mismatch");
}

void check(const HLD &h, const ColorMax &t)
{
    states++;
    for (int u = 1; u <= h.n; u++)
    {
        vector<int> seen(h.n + 1);
        vector<int> q{u};
        seen[u] = 1;
        long long ans = LLONG_MIN;
        int highest = u;
        for (size_t i = 0; i < q.size(); i++)
        {
            int v = q[i];
            ans = max(ans, t.weight[v]);
            if (h.dep[v] < h.dep[highest]) highest = v;
            for (int w : h.g[v])
            {
                if (seen[w] || t.col[w] != t.col[u]) continue;
                seen[w] = 1;
                q.push_back(w);
            }
        }
        require(t.query(u) == ans);
        require(t.top(u) == highest);
        q = {u};
        ans = LLONG_MIN;
        for (size_t i = 0; i < q.size(); i++)
        {
            int v = q[i];
            ans = max(ans, t.weight[v]);
            for (int w : h.g[v])
            {
                if (h.fa[w] == v && w != v && t.col[w] == t.col[u])
                    q.push_back(w);
            }
        }
        require(t.down(u) == ans);
        for (int c = 0; c < 2; c++)
        {
            multiset<long long> expected;
            for (int v : h.g[u])
            {
                if (h.fa[v] != u || v == u || v == h.son[u] || t.col[v] != c)
                    continue;
                q = {v};
                ans = LLONG_MIN;
                for (size_t i = 0; i < q.size(); i++)
                {
                    int x = q[i];
                    ans = max(ans, t.weight[x]);
                    for (int w : h.g[x])
                    {
                        if (h.fa[w] == x && w != x && t.col[w] == c)
                            q.push_back(w);
                    }
                }
                expected.insert(ans);
            }
            require(t.light[u][c] == expected);
        }
    }
}

vector<pair<int, int>> prufer(int n, int code)
{
    vector<int> a(max(0, n - 2));
    vector<int> deg(n + 1, 1);
    for (int &v : a)
    {
        v = code % n + 1;
        code /= n;
        deg[v]++;
    }
    vector<pair<int, int>> edges;
    for (int v : a)
    {
        int u = 1;
        while (deg[u] != 1) u++;
        edges.emplace_back(u, v);
        deg[u]--;
        deg[v]--;
    }
    int last = 0;
    for (int u = 1; u <= n; u++)
    {
        if (deg[u] != 1) continue;
        if (last) edges.emplace_back(last, u);
        last = u;
    }
    return edges;
}

int main(int argc, char **argv)
{
    if (argc > 1 && string(argv[1]) == "large")
    {
        int n = 100000;
        for (int shape = 0; shape < 3; shape++)
        {
            HLD h(n);
            for (int u = 2; u <= n; u++)
                h.add(u, shape == 0 ? u - 1 : shape == 1 ? 1 : u / 2);
            h.build(shape == 0 ? n : 1);
            vector<int> col(n + 1);
            vector<long long> w(n + 1, 1);
            w[n] = 7;
            ColorMax t(h, col, w);
            require(t.query(1) == 7);
            if (shape == 0)
            {
                t.flip(n / 2);
                require(t.query(1) == 1);
                require(t.query(n / 2) == 1);
                require(t.query(n) == 7);
                t.flip(n / 2);
            }
            for (int i = 0; i < 100000; i++)
            {
                t.flip(1);
                t.set_weight(1, i % 2 ? 2 : 3);
                require(t.query(1) == (i % 2 ? 7 : 3));
                require(t.query(n) == 7);
            }
            t.set_weight(n, LLONG_MIN);
            require(t.query(n) == 2);
            t.set_weight(n, LLONG_MAX);
            require(t.query(1) == LLONG_MAX);
        }
        cout << "large chain/star/binary PASS\n";
        return 0;
    }
    vector<long long> values{LLONG_MIN, LLONG_MAX, -1, 0, 1, 5, 5};
    for (int n = 1; n <= 5; n++)
    {
        int trees = 1;
        for (int i = 0; i < n - 2; i++) trees *= n;
        int patterns = 6;
        if (n <= 3)
        {
            patterns = 1;
            for (int i = 0; i < n; i++) patterns *= 3;
        }
        for (int code = 0; code < trees; code++)
        {
            HLD h(n);
            for (auto [u, v] : prufer(n, code)) h.add(u, v);
            for (int r = 1; r <= n; r++)
            {
                h.build(r);
                for (int mask = 0; mask < (1 << n); mask++)
                {
                    for (int pattern = 0; pattern < patterns; pattern++)
                    {
                        vector<int> col(n + 1);
                        vector<long long> w(n + 1);
                        int digits = pattern;
                        for (int u = 1; u <= n; u++)
                        {
                            col[u] = mask >> (u - 1) & 1;
                            w[u] = n <= 3 ? values[digits % 3] : values[(pattern + (pattern % 2 ? u : 0)) % values.size()];
                            digits /= 3;
                        }
                        ColorMax t(h, col, w);
                        check(h, t);
                        for (int u = 1; u <= n; u++)
                        {
                            t.flip(u);
                            check(h, t);
                            t.set_weight(u, values[(u + pattern) % values.size()]);
                            check(h, t);
                            t.flip(u);
                            check(h, t);
                            t.set_weight(u, w[u]);
                            check(h, t);
                        }
                    }
                }
            }
        }
    }
    mt19937 rng(20261012);
    for (int test = 0; test < 20; test++)
    {
        int n = 200;
        HLD h(n);
        for (int u = 2; u <= n; u++) h.add(u, rng() % (u - 1) + 1);
        h.build(rng() % n + 1);
        vector<int> col(n + 1);
        vector<long long> w(n + 1);
        for (int u = 1; u <= n; u++)
        {
            col[u] = rng() % 2;
            w[u] = values[rng() % values.size()];
        }
        ColorMax t(h, col, w);
        check(h, t);
        for (int i = 0; i < 500; i++)
        {
            int u = rng() % n + 1;
            if (rng() % 2) t.flip(u);
            else t.set_weight(u, values[rng() % values.size()]);
            check(h, t);
        }
    }
    cout << states << " exhaustive/random states PASS\n";
}
