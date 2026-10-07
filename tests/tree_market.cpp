#include "../src/compact/tree_market.hpp"
using I = __int128_t;
using Edge = tuple<int, int, long long>;
long long cases = 0, checks = 0;

void require(bool ok)
{
    checks++;
    if (!ok) throw runtime_error("oracle mismatch");
}

vector<int> oracle(int n, const vector<Edge> &edges, const vector<int> &market)
{
    const I inf = I(1) << 120;
    vector<vector<I>> d(n, vector<I>(n, inf));
    for (int u = 0; u < n; u++) d[u][u] = 0;
    for (auto [u, v, w] : edges) d[u][v] = d[v][u] = w;
    for (int k = 0; k < n; k++)
        for (int u = 0; u < n; u++)
            for (int v = 0; v < n; v++) d[u][v] = min(d[u][v], d[u][k] + d[k][v]);
    vector<int> answer(n);
    for (int x = 0; x < n; x++)
        if (!market[x])
            for (int v = 0; v < n; v++)
            {
                pair<I, int> old{inf, n};
                for (int m = 0; m < n; m++)
                    if (market[m]) old = min(old, pair<I, int>{d[v][m], m});
                answer[x] += pair<I, int>{d[v][x], x} < old;
            }
    return answer;
}

vector<Edge> decode(int n, vector<int> code, int pattern)
{
    vector<int> degree(n, 1);
    for (int u : code) degree[u]++;
    vector<Edge> edges;
    auto add = [&](int u, int v)
    {
        edges.push_back({u, v, pattern ? (u + v) % 3 : 0});
    };
    for (int v : code)
    {
        int u = find(degree.begin(), degree.end(), 1) - degree.begin();
        add(u, v);
        degree[u]--;
        degree[v]--;
    }
    vector<int> last;
    for (int u = 0; u < n; u++)
        if (degree[u] == 1) last.push_back(u);
    if (last.size() == 2) add(last[0], last[1]);
    return edges;
}

void check(int n, const vector<Edge> &edges, const vector<vector<int>> &markets)
{
    TreeMarket tree(n);
    for (auto [u, v, w] : edges) tree.add(u, v, w);
    for (const auto &m : markets)
    {
        auto want = oracle(n, edges, m);
        require(tree.solve(m) == want);
        require(tree.answer == want);
        cases++;
    }
}

int main(int argc, char **)
{
    try
    {
        for (int n = 1; n <= 5; n++)
        {
            int total = 1;
            for (int i = 0; i < n - 2; i++) total *= n;
            for (int code = 0; code < total; code++)
                for (int pattern = 0; pattern < 2; pattern++)
                {
                    vector<int> a(max(0, n - 2));
                    int x = code;
                    for (int &v : a)
                    {
                        v = x % n;
                        x /= n;
                    }
                    vector<vector<int>> markets;
                    for (int mask = 0; mask < (1 << n); mask++)
                    {
                        vector<int> m(n);
                        for (int u = 0; u < n; u++) m[u] = (mask >> u) & 1;
                        markets.push_back(m);
                    }
                    check(n, decode(n, a, pattern), markets);
                }
        }
        mt19937 rng(50162026);
        for (int rep = 0; rep < 600; rep++)
        {
            int n = 1 + rng() % 25;
            vector<Edge> edges;
            for (int v = 1; v < n; v++) edges.push_back({rng() % v, v, rng() % 10});
            shuffle(edges.begin(), edges.end(), rng);
            vector<vector<int>> markets(3, vector<int>(n));
            for (auto &m : markets)
                for (int &x : m) x = rng() % 3 == 0;
            check(n, edges, markets);
        }
        check(4, {{0, 1, LLONG_MAX}, {1, 2, LLONG_MAX}, {2, 3, LLONG_MAX}},
              {{1, 0, 0, 0}, {0, 0, 0, 1}, {1, 0, 0, 1}, {0, 0, 0, 0}});
        if (argc == 1)
        {
            int n = 100000;
            for (int shape = 0; shape < 3; shape++)
            {
                TreeMarket tree(n);
                for (int v = 1; v < n; v++) tree.add(shape == 1 ? 0 : v - 1, v, shape == 2 ? 0 : 1);
                vector<int> market(n);
                market[shape == 2 ? n - 1 : 0] = 1;
                auto result = tree.solve(market);
                for (int u = 0; u < n; u++)
                {
                    int want = market[u] ? 0 : shape == 0 ? n - u / 2 - 1 : shape == 1 ? 1 : n;
                    require(result[u] == want);
                }
                require(tree.solve(vector<int>(n)) == vector<int>(n, n));
                require(tree.solve(vector<int>(n, 1)) == vector<int>(n));
            }
        }
        cout << "PASS " << cases << " scenarios " << checks << " checks\n";
    }
    catch (const exception &)
    {
        cout << "ORACLE_REJECT\n";
    }
}
