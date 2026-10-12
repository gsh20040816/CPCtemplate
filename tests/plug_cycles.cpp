#include "../src/compact/plug_cycles.hpp"
#include "../src/compact/plug_cycle.hpp"
#include <boost/multiprecision/cpp_int.hpp>
using boost::multiprecision::cpp_int;

void require(bool ok)
{
    if (!ok) abort();
}

struct Oracle
{
    int n, m;
    vector<vector<int>> g;
    vector<vector<int>> cycles;
    vector<long long> all, separate;
    unsigned long long full = 0;

    bool inside(int p, const vector<int> &polygon)
    {
        bool answer = false;
        for (int i = 0; i < (int)polygon.size(); i++)
        {
            int u = polygon[i];
            int v = polygon[(i + 1) % polygon.size()];
            if ((u / m > p / m) != (v / m > p / m))
                if (u % m > p % m) answer = !answer;
        }
        return answer;
    }
    void cover(unsigned long long used)
    {
        if (used == full)
        {
            int k = cycles.size();
            all[k]++;
            bool nested = false;
            for (int i = 0; i < k; i++)
                for (int j = 0; j < k; j++)
                    if (i != j && inside(cycles[i][0], cycles[j])) nested = true;
            if (!nested) separate[k]++;
            return;
        }
        int start = __builtin_ctzll(full ^ used);
        vector<int> path{start};
        walk(start, start, used | (1ULL << start), path);
    }
    void walk(int start, int u, unsigned long long used, vector<int> &path)
    {
        for (int v : g[u])
        {
            if (v == start)
            {
                if (path.size() >= 4 && path[1] < u)
                {
                    cycles.push_back(path);
                    cover(used);
                    cycles.pop_back();
                }
            }
            else if (!(used >> v & 1))
            {
                path.push_back(v);
                walk(start, v, used | (1ULL << v), path);
                path.pop_back();
            }
        }
    }
    explicit Oracle(const vector<string> &a)
    {
        n = a.size();
        m = a[0].size();
        require(n * m <= 64);
        g.resize(n * m);
        all.resize(n * m / 4 + 1);
        separate = all;
        for (int i = 0; i < n; i++)
        {
            for (int j = 0; j < m; j++)
            {
                if (a[i][j] != '.') continue;
                int u = i * m + j;
                full |= 1ULL << u;
                for (auto [di, dj] : vector<pair<int, int>>{{0, 1}, {0, -1}, {1, 0}, {-1, 0}})
                {
                    int x = i + di;
                    int y = j + dj;
                    if (x >= 0 && x < n && y >= 0 && y < m && a[x][y] == '.')
                        g[u].push_back(x * m + y);
                }
            }
        }
        cover(0);
    }
};

long long checks = 0;
void check(const vector<string> &a)
{
    Oracle truth(a);
    for (int k = 0; k <= (int)truth.all.size(); k++)
    {
        long long all = k < (int)truth.all.size() ? truth.all[k] : 0;
        long long separate = k < (int)truth.all.size() ? truth.separate[k] : 0;
        auto x = grid_cycles<long long>(a, k, true);
        auto y = grid_cycles<long long>(a, k);
        if (x != all || y != separate)
        {
            for (auto row : a) cerr << row << '\n';
            cerr << "k=" << k << " got " << x << ',' << y << " expected " << all << ',' << separate << '\n';
            abort();
        }
        checks += 2;
    }
    require(grid_cycles<long long>(a, 1) == grid_cycle<long long>(a));
}

int main()
{
    int boards = 0;
    for (int n = 1; n <= 4; n++)
    {
        for (int m = 1; m <= 4; m++)
        {
            for (unsigned mask = 0; mask < (1U << (n * m)); mask++)
            {
                vector<string> a(n, string(m, '*'));
                for (int u = 0; u < n * m; u++)
                    if (mask >> u & 1) a[u / m][u % m] = '.';
                check(a);
                boards++;
            }
        }
    }
    mt19937 rng(20261012);
    for (int t = 0; t < 300; t++)
    {
        vector<string> a(5, string(5, '*'));
        for (auto &row : a)
            for (char &c : row)
                if (rng() % 100 < 62) c = '.';
        check(a);
        boards++;
    }
    vector<string> rings(6, string(6, '*'));
    for (int i = 0; i < 6; i++)
        rings[0][i] = rings[5][i] = rings[i][0] = rings[i][5] = '.';
    rings[2][2] = rings[2][3] = rings[3][2] = rings[3][3] = '.';
    check(rings);
    require(grid_cycles<long long>(rings, 2, true) == 1);
    require(grid_cycles<long long>(rings, 2) == 0);
    // Three nested forced rings: rejecting only completed pairs is insufficient.
    vector<string> triple(10, string(10, '*'));
    for (int d : {0, 2, 4})
        for (int t = d; t < 10 - d; t++)
            triple[d][t] = triple[9 - d][t] = triple[t][d] = triple[t][9 - d] = '.';
    require(grid_cycles<long long>(triple, 3, true) == 1);
    require(grid_cycles<long long>(triple, 3) == 0);
    require(grid_cycles<long long>({}, 0) == 1);
    require(grid_cycles<long long>({""}, 0) == 1);
    require(grid_cycles<long long>({""}, 1) == 0);
    // 2 x 4 has one one-cycle and one two-cycle cover; separated blocks multiply.
    vector<string> blocks(2, "");
    for (int t = 0; t < 70; t++)
    {
        for (auto &row : blocks) row += "....*";
    }
    cpp_int choose = 1;
    for (int t = 1; t <= 35; t++) choose = choose * (70 - t + 1) / t;
    require(grid_cycles<cpp_int>(blocks, 105) == choose);
    // All 16 slots are reachable in a 15-column border ring.
    vector<string> border(15, string(15, '*'));
    for (int i = 0; i < 15; i++)
        border[0][i] = border[14][i] = border[i][0] = border[i][14] = '.';
    require(grid_cycles<long long>(border, 1) == 1);
    cout << "PASS " << boards << " boards, " << checks << " independent counts; nesting, width15, cpp_int\n";
}
