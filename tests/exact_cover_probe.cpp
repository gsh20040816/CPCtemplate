#include "../src/compact/exact_cover.hpp"
#include <algorithm>
#include <iostream>
#include <random>
#include <stdexcept>

long long checks = 0, cases = 0;
void require(bool ok)
{
    checks++;
    if (!ok) throw runtime_error("oracle mismatch");
}

bool brute(int m, const vector<vector<int>> &r)
{
    for (unsigned mask = 0; mask < (1u << r.size()); mask++)
    {
        vector<int> s(m);
        for (int i = 0; i < int(r.size()); i++)
            if (mask >> i & 1) for (int c : r[i]) s[c]++;
        if (all_of(s.begin(), s.end(), [](int x) { return x == 1; })) return true;
    }
    return false;
}

void check(int m, const vector<vector<int>> &r, int expected = -1)
{
    cases++;
    bool want = expected < 0 ? brute(m, r) : expected;
    auto input = r;
    ExactCover d(m, r);
    auto a = d.a;
    auto s = d.s;
    auto inspect = [&](ExactCover &x)
    {
        auto ans = x.solve();
        require(bool(ans) == want);
        if (ans)
        {
            vector<int> count(m), used(r.size());
            for (int i : *ans)
            {
                require(0 <= i && i < int(r.size()));
                require(!used[i]++ && !r[i].empty());
                for (int c : r[i]) count[c]++;
            }
            for (int v : count) require(v == 1);
        }
        require(x.s == s && x.a.size() == a.size());
        for (size_t i = 0; i < a.size(); i++)
            require(x.a[i].l == a[i].l && x.a[i].r == a[i].r &&
                    x.a[i].u == a[i].u && x.a[i].d == a[i].d &&
                    x.a[i].c == a[i].c && x.a[i].row == a[i].row);
    };
    for (int i = 0; i < 3; i++) inspect(d);
    auto copy = d;
    inspect(copy);
    require(r == input);
    d = ExactCover(1, {{0}});
    require(d.solve() == optional<vector<int>>({0}));
    d = ExactCover(1, {{}});
    require(!d.solve());
    d = ExactCover(0, {{}, {}});
    require(d.solve() && d.solve()->empty());
}

int main()
{
    try
    {
        for (int n = 0; n <= 5; n++)
            for (int m = 0; m <= 5; m++)
                if (n * m <= 16)
                    for (unsigned bits = 0; bits < (1u << (n * m)); bits++)
                    {
                        vector<vector<int>> r(n);
                        for (int i = 0; i < n; i++)
                            for (int j = 0; j < m; j++)
                                if (bits >> (i * m + j) & 1) r[i].push_back(j);
                        check(m, r);
                    }
        mt19937 rng(4929);
        for (int t = 0; t < 1000; t++)
        {
            int m = rng() % 10, n = rng() % 12;
            vector<vector<int>> r(n);
            for (auto &row : r)
                for (int c = 0; c < m; c++)
                    if (rng() % 3 == 0) row.push_back(c);
            check(m, r);
            for (auto &row : r) shuffle(row.begin(), row.end(), rng);
            shuffle(r.begin(), r.end(), rng);
            check(m, r);
        }
        check(7, {{2, 4, 5}, {0, 3, 6}, {1, 2, 5}, {0, 3}, {1, 6}, {3, 4, 6}});
        check(3, {{0, 1}, {1, 2}, {0, 2}});
        check(2, {{}, {1}, {}, {0}, {1}});
        check(3, {{0}, {1}, {2}, {0, 1, 2}});
        vector<vector<int>> identity(500), blocks(500);
        for (int i = 0; i < 500; i++)
        {
            identity[i] = {i};
            for (int j = i / 10 * 10; j < i / 10 * 10 + 10; j++) blocks[i].push_back(j);
        }
        check(500, identity, 1);
        check(500, blocks, 1);
        for (auto &r : blocks) shuffle(r.begin(), r.end(), rng);
        shuffle(blocks.begin(), blocks.end(), rng);
        check(500, blocks, 1);
        identity.resize(497);
        identity.push_back({497, 498}); identity.push_back({498, 499}); identity.push_back({497, 499});
        check(500, identity, 0);
        check(500, vector<vector<int>>(500), 0);
        cout << "PASS " << cases << " cases " << checks << " checks\n";
    }
    catch (const runtime_error &)
    {
        cout << "ORACLE_REJECT\n";
    }
}
