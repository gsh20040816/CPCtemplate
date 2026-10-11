#include "../src/compact/tutte.hpp"

int power(int a, int b)
{
    int result = 1;
    while (b-- > 0) result = (long long)result * a % 998244353;
    return result;
}

int brute(const vector<unsigned> &g, int x, int y)
{
    int n = g.size();
    vector<pair<int, int>> edges;
    for (int u = 0; u < n; u++)
        for (int v = u + 1; v < n; v++)
            if (g[u] >> v & 1) edges.push_back({u, v});
    auto components = [&](int mask)
    {
        vector<vector<int>> adj(n);
        for (int i = 0; i < (int)edges.size(); i++)
            if (mask >> i & 1)
            {
                auto [u, v] = edges[i];
                adj[u].push_back(v);
                adj[v].push_back(u);
            }
        vector<int> seen(n);
        auto dfs = [&](auto &&self, int u) -> void
        {
            seen[u] = 1;
            for (int v : adj[u])
                if (!seen[v]) self(self, v);
        };
        int count = 0;
        for (int u = 0; u < n; u++)
            if (!seen[u])
            {
                count++;
                dfs(dfs, u);
            }
        return count;
    };
    int all = (1 << edges.size()) - 1;
    int base = components(all);
    int answer = 0;
    for (int mask = 0; mask <= all; mask++)
    {
        int c = components(mask);
        int a = power((x + 998244352LL) % 998244353, c - base);
        int b = power((y + 998244352LL) % 998244353, c + popcount((unsigned)mask) - n);
        answer = (answer + (long long)a * b) % 998244353;
    }
    return answer;
}

void check(const vector<unsigned> &g, int x, int y)
{
    int a = tutte(g, x, y), b = brute(g, x, y);
    if (a != b)
    {
        cerr << "Mismatch n=" << g.size() << " x=" << x << " y=" << y << " got=" << a << " expected=" << b << endl;
        abort();
    }
}

int main()
{
    vector<int> values = {0, 1, 2, 998244352};
    int graphs = 0;
    for (int n = 0; n <= 4; n++)
        for (int mask = 0; mask < (1 << (n * (n - 1) / 2)); mask++)
        {
            vector<unsigned> g(n);
            int id = 0;
            for (int u = 0; u < n; u++)
                for (int v = u + 1; v < n; v++)
                    if (mask >> id++ & 1)
                    {
                        g[u] |= 1U << v;
                        g[v] |= 1U << u;
                    }
            for (int x : values)
                for (int y : values) check(g, x, y);
            graphs++;
        }
    mt19937 rng(45);
    for (int test = 0; test < 500; test++)
    {
        int n = rng() % 8 + 1;
        vector<unsigned> g(n);
        int m = 0;
        for (int u = 0; u < n; u++)
            for (int v = u + 1; v < n; v++)
                if (rng() % 3 == 0 && m < 14)
                {
                    g[u] |= 1U << v;
                    g[v] |= 1U << u;
                    m++;
                }
        check(g, rng() % 998244353, rng() % 998244353);
        check(g, 1, 1);
        check(g, 0, 0);
    }
    vector<unsigned> sample = {22,25,25,6,7};
    for (auto [x,y,w] : vector<array<int,3>>{{0,1,6},{0,2,24},{1,0,10},{1,1,24},{1,2,52},{2,0,60},{2,1,86}})
        if (tutte(sample,x,y) != w) abort();
    cout << "PASS: " << graphs << " simple graphs through n=4 at 16 boundary evaluations; 500 random graphs with edge-subset oracle; seven official sample evaluations\n";
}
