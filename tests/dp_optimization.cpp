#include "../src/compact/monotone_hull.hpp"
#include "../src/compact/monotone_dp.hpp"
#include "../src/compact/wqs_independent_set.hpp"
#include <cstdlib>
#include <iostream>
#include <random>
using namespace std;

void check(bool ok)
{
    if (!ok) abort();
}

int main()
{
    mt19937 rng(2365321);
    for (int test = 0; test < 3000; test++)
    {
        MonotoneHull hull;
        vector<MonotoneHull::Line> lines;
        long long m = 100, x = -100;
        for (int step = 0; step < 150; step++)
        {
            if (lines.empty() || rng() % 2)
            {
                m -= rng() % 4;
                long long b = int(rng() % 1001) - 500;
                int id = lines.size();
                hull.add(m, b, id);
                lines.push_back({m, b, id});
            }
            else
            {
                x += rng() % 4;
                auto want = make_pair(lines[0].value(x), lines[0].id);
                for (auto line : lines) want = min(want, make_pair(line.value(x), line.id));
                check(hull.query(x) == want);
            }
        }
    }
    MonotoneHull boundary;
    boundary.add(1000000000000000000LL, -1000000000000000000LL, 0);
    boundary.add(0, 1000000000000000000LL, 1);
    boundary.add(-1000000000000000000LL, -1000000000000000000LL, 2);
    check(boundary.query(-1000000000000000000LL).second == 0);
    check(boundary.query(0).second == 0);
    check(boundary.query(1000000000000000000LL).second == 2);
    for (int test = 0; test < 500; test++)
    {
        int n = 1 + rng() % 35;
        vector<vector<int>> a(n + 1, vector<int>(n + 1));
        for (int i = 1; i <= n; i++)
        {
            for (int j = 1; j < i; j++) a[i][j] = a[j][i] = rng() % 10;
        }
        vector<vector<long long>> cost(n + 1, vector<long long>(n + 1));
        for (int l = 1; l <= n; l++)
        {
            for (int r = l; r <= n; r++)
            {
                cost[l][r] = cost[l][r - 1];
                for (int j = l; j < r; j++) cost[l][r] += a[j][r];
            }
        }
        vector<long long> prev(n + 1, LLONG_MAX / 4);
        prev[0] = 0;
        for (int g = 1; g <= n; g++)
        {
            vector<int> opt;
            auto got = monotone_dp_layer(prev, g, [&](int l, int r) { return cost[l][r]; }, opt);
            for (int i = g; i <= n; i++)
            {
                pair<long long, int> want{LLONG_MAX / 4, -1};
                for (int j = g - 1; j < i; j++)
                {
                    if (prev[j] == LLONG_MAX / 4) continue;
                    want = min(want, make_pair(prev[j] + cost[j + 1][i], j));
                }
                check(got[i] == want.first && opt[i] == want.second);
            }
            prev = got;
        }
    }
    {
        vector<long long> prev{0, -1, -2, -3};
        vector<int> opt;
        auto got = monotone_dp_layer(prev, 1, [](int, int) { return 0LL; }, opt);
        check(got[1] == 0 && got[2] == -1 && got[3] == -2);
        check(opt[1] == 0 && opt[2] == 1 && opt[3] == 2);
        MonotoneHull ties;
        ties.add(1, 0, 99);
        ties.add(1, 0, -8);
        ties.add(0, 0, -9);
        check(ties.query(0).second == 99);
        check(ties.query(1).second == -9);
    }
    for (int test = 0; test < 1200; test++)
    {
        int n = rng() % 17;
        vector<long long> a(n);
        for (auto &x : a) x = int(rng() % 31) - 15;
        vector<long long> exact(n + 1, LLONG_MIN);
        for (int mask = 0; mask < (1 << n); mask++)
        {
            if (mask & (mask << 1)) continue;
            long long value = 0;
            for (int i = 0; i < n; i++)
            {
                if (mask >> i & 1) value += a[i];
            }
            int count = __builtin_popcount(unsigned(mask));
            exact[count] = max(exact[count], value);
        }
        long long best = 0;
        for (int k = 0; k <= n; k++)
        {
            best = max(best, exact[k]);
            check(wqs_independent_set(a, k) == best);
        }
    }
    cout << "PASS hull streams, all partition layers and exhaustive path independent sets\n";
}
