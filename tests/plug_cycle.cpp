#include "../src/compact/plug_cycle.hpp"
#include <boost/multiprecision/cpp_int.hpp>
using boost::multiprecision::cpp_int;

long long brute(const vector<string> &a)
{
    int n = a.size();
    int m = a[0].size();
    vector<vector<int>> id(n, vector<int>(m, -1));
    int count = 0;
    for (int i = 0; i < n; i++)
        for (int j = 0; j < m; j++)
            if (a[i][j] == '.') id[i][j] = count++;
    if (count < 4 || count % 2) return 0;
    vector<vector<int>> g(count);
    for (int i = 0; i < n; i++)
        for (int j = 0; j < m; j++)
        {
            if (id[i][j] == -1) continue;
            for (auto [di, dj] : vector<pair<int, int>>{{0, 1}, {1, 0}})
            {
                int x = i + di;
                int y = j + dj;
                if (x >= n || y >= m || id[x][y] == -1) continue;
                g[id[i][j]].push_back(id[x][y]);
                g[id[x][y]].push_back(id[i][j]);
            }
        }
    for (auto &e : g)
        if (e.size() < 2) return 0;
    long long answer = 0;
    auto dfs = [&](auto &&self, int u, unsigned long long seen) -> void
    {
        if (__builtin_popcountll(seen) == count)
        {
            for (int v : g[u])
                if (v == 0) answer++;
            return;
        }
        for (int v : g[u])
            if (!(seen >> v & 1)) self(self, v, seen | (1ULL << v));
    };
    dfs(dfs, 0, 1);
    return answer / 2;
}

void check(vector<string> a)
{
    long long want = brute(a);
    if (grid_cycle<long long>(a) != want || grid_cycle<cpp_int>(a) != want)
    {
        for (auto row : a) cerr << row << '\n';
        cerr << "want " << want << '\n';
        abort();
    }
}

int main()
{
    if (grid_cycle<cpp_int>({}) != 0) abort();
    if (grid_cycle<cpp_int>({"", ""}) != 0) abort();
    int cases = 0;
    for (int n = 1; n <= 4; n++)
        for (int m = 1; m <= 4; m++)
            for (int mask = 0; mask < (1 << (n * m)); mask++)
            {
                vector<string> a(n, string(m, '*'));
                for (int i = 0; i < n; i++)
                    for (int j = 0; j < m; j++)
                        if (mask >> (i * m + j) & 1) a[i][j] = '.';
                check(a);
                cases++;
            }
    mt19937 rng(5056);
    for (int test = 0; test < 500; test++)
    {
        vector<string> a(5, string(5, '*'));
        int count = 0;
        for (auto &row : a)
            for (char &c : row)
                if (rng() % 2 && count < 18)
                {
                    c = '.';
                    count++;
                }
        check(a);
    }
    // Two disconnected squares cannot count as one cycle.
    check({"..*..", "..*.."});
    for (int n : {2, 3, 12, 15, 30})
    {
        vector<string> a(n, string(15, '*'));
        for (int i = 0; i < n; i++)
            for (int j = 0; j < 15; j++)
                if (i == 0 || i == n - 1 || j == 0 || j == 14) a[i][j] = '.';
        if (grid_cycle<cpp_int>(a) != 1) abort();
    }
    cout << cases << " exhaustive obstacle grids, 500 random grids, width15 border cycles PASS\n";
}
