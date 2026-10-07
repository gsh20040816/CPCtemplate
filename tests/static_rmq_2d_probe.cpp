#include "../src/compact/static_rmq_2d.hpp"
#include <iostream>
#include <random>
#include <cstdlib>
long long queries = 0;

void require(bool ok)
{
    if (!ok)
    {
        cout << "ORACLE_REJECT\n";
        exit(0);
    }
}

void check(const vector<vector<long long>> &a)
{
    StaticRMQ2D<long long> mn(a);
    StaticRMQ2D<long long, greater<long long>> mx(a);
    int n = a.size(), m = n ? a[0].size() : 0;
    require(mn.a == a && mx.a == a);
    for (int x1 = 0; x1 < n; x1++)
    {
        for (int y1 = 0; y1 < m; y1++)
        {
            for (int x2 = x1 + 1; x2 <= n; x2++)
            {
                for (int y2 = y1 + 1; y2 <= m; y2++)
                {
                    pair<int, int> low{x1, y1}, high = low;
                    for (int x = x1; x < x2; x++)
                    {
                        for (int y = y1; y < y2; y++)
                        {
                            if (a[x][y] < a[low.first][low.second]) low = {x, y};
                            if (a[x][y] > a[high.first][high.second]) high = {x, y};
                        }
                    }
                    require(mn.query(x1, y1, x2, y2) == low);
                    require(mx.query(x1, y1, x2, y2) == high);
                    queries++;
                }
            }
        }
    }
}

struct Record
{
    long long key;
    int payload;
};

struct ByKey
{
    bool reverse;
    long long *calls;

    bool operator()(const Record &x, const Record &y) const
    {
        (*calls)++;
        return reverse ? x.key > y.key : x.key < y.key;
    }
};

int main()
{
    check({});
    check(vector<vector<long long>>(3));
    mt19937_64 rng(279);
    for (int n = 1; n <= 3; n++)
    {
        for (int m = 1; m <= 3; m++)
        {
            for (int mask = 0; mask < (1 << (n * m)); mask++)
            {
                vector<vector<long long>> a(n, vector<long long>(m));
                for (int x = 0; x < n; x++)
                {
                    for (int y = 0; y < m; y++) a[x][y] = mask >> (x * m + y) & 1;
                }
                check(a);
            }
        }
    }
    vector<long long> pool{LLONG_MIN, -1, 0, 1, LLONG_MAX};
    for (auto [n, m] : vector<pair<int, int>>{{1, 65}, {65, 1}, {2, 33}, {33, 2}, {7, 8}, {8, 9}, {15, 16}, {16, 17}})
    {
        vector<vector<long long>> a(n, vector<long long>(m));
        for (auto &row : a)
        {
            for (auto &x : row) x = pool[rng() % pool.size()];
        }
        check(a);
        for (auto &row : a) fill(row.begin(), row.end(), 0);
        check(a);
    }
    for (int test = 0; test < 100; test++)
    {
        int n = 1 + rng() % 12, m = 1 + rng() % 12;
        vector<vector<long long>> a(n, vector<long long>(m));
        for (auto &row : a)
        {
            for (auto &x : row) x = pool[rng() % pool.size()];
        }
        check(a);
    }
    int n = 305, m = 305;
    vector<vector<Record>> a(n, vector<Record>(m));
    for (int x = 0; x < n; x++)
    {
        for (int y = 0; y < m; y++) a[x][y] = {x * m + y, x ^ y};
    }
    for (bool reverse : {false, true})
    {
        long long calls = 0;
        StaticRMQ2D<Record, ByKey> rmq(a, {reverse, &calls});
        require(rmq.st.size() == 9 && rmq.st[0].size() == 9);
        size_t cells = 0;
        for (const auto &level : rmq.st)
        {
            for (const auto &v : level) cells += v.size();
        }
        require(cells == size_t(n) * m * 81 && calls <= 2 * (long long)cells);
        for (int q = 0; q < 100000; q++)
        {
            int x1 = rng() % n, x2 = rng() % n, y1 = rng() % m, y2 = rng() % m;
            if (x1 > x2) swap(x1, x2);
            if (y1 > y2) swap(y1, y2);
            long long before = calls;
            auto got = rmq.query(x1, y1, x2 + 1, y2 + 1);
            auto want = reverse ? make_pair(x2, y2) : make_pair(x1, y1);
            require(got == want && calls - before <= 6);
            require(rmq.a[got.first][got.second].payload == (want.first ^ want.second));
        }
    }
    cout << "PASS " << queries << " independently scanned rectangles and 200000 large analytic queries\n";
}
