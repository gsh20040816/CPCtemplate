#include "../src/compact/color_components.hpp"

long long states = 0;

void require(bool ok)
{
    if (!ok) throw runtime_error("ColorComponents oracle mismatch");
}

void check(const HLD &h, const ColorComponents &t)
{
    states++;
    for (int u = 1; u <= h.n; u++)
    {
        vector<int> seen(h.n + 1);
        vector<int> q{u};
        seen[u] = 1;
        int highest = u;
        for (size_t i = 0; i < q.size(); i++)
        {
            int v = q[i];
            if (h.dep[v] < h.dep[highest]) highest = v;
            for (int w : h.g[v])
            {
                if (seen[w] || t.col[w] != t.col[u]) continue;
                seen[w] = 1;
                q.push_back(w);
            }
        }
        require(t.query(u) == int(q.size()));
        require(t.top(u) == highest);
        for (int c = 0; c < 2; c++)
        {
            q = {u};
            for (size_t i = 0; i < q.size(); i++)
            {
                int v = q[i];
                for (int w : h.g[v])
                {
                    if (h.fa[w] == v && w != v && t.col[w] == c)
                        q.push_back(w);
                }
            }
            require(t.value(u, c) == int(q.size()));
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
    bool large = argc > 1 && string(argv[1]) == "large";
    if (large)
    {
        int n = 100000;
        for (int shape = 0; shape < 3; shape++)
        {
            HLD h(n);
            for (int u = 2; u <= n; u++)
                h.add(u, shape == 0 ? u - 1 : shape == 1 ? 1 : u / 2);
            h.build(shape == 0 ? n : 1);
            ColorComponents t(h);
            require(t.query(n) == n);
            if (shape == 0)
            {
                int mid = n / 2;
                t.flip(mid);
                require(t.query(1) == mid - 1);
                require(t.query(mid) == 1);
                require(t.query(n) == n - mid);
                t.flip(mid);
            }
            for (int i = 0; i < 100000; i++)
            {
                t.flip(1);
                require(t.query(1) == (i % 2 ? n : 1));
                if (shape == 1) require(t.query(n) == (i % 2 ? n : 1));
            }
            require(t.query(n) == n);
        }
        cout << "large chain/star/binary pass\n";
        return 0;
    }
    for (int n = 1; n <= 6; n++)
    {
        int trees = 1;
        for (int i = 0; i < n - 2; i++) trees *= n;
        for (int code = 0; code < trees; code++)
        {
            HLD h(n);
            for (auto [u, v] : prufer(n, code)) h.add(u, v);
            int roots = n <= 5 ? n : 1;
            for (int r = 1; r <= roots; r++)
            {
                h.build(n <= 5 ? r : code % n + 1);
                for (int mask = 0; mask < (1 << n); mask++)
                {
                    vector<int> col(n + 1);
                    for (int u = 1; u <= n; u++) col[u] = mask >> (u - 1) & 1;
                    ColorComponents t(h, col);
                    check(h, t);
                    for (int u = 1; u <= n; u++)
                    {
                        t.flip(u);
                        check(h, t);
                        t.flip(u);
                        check(h, t);
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
        for (int u = 1; u <= n; u++) col[u] = rng() % 2;
        ColorComponents t(h, col);
        check(h, t);
        for (int i = 0; i < 500; i++)
        {
            t.flip(rng() % n + 1);
            check(h, t);
        }
    }
    cout << states << " exhaustive/random states pass\n";
}
