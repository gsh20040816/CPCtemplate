#include "../src/compact/minimum_cover.hpp"
#include <iostream>
#include <numeric>
#include <random>
#include <stdexcept>

long long cases = 0, checks = 0, residuals = 0;
void require(bool ok)
{
    checks++;
    if (!ok) throw runtime_error("oracle mismatch");
}

int brute(int m, const vector<vector<int>> &rows, unsigned required)
{
    int best = m + 1;
    vector<unsigned> unions(1u << rows.size());
    for (unsigned bits = 0; bits < unions.size(); bits++)
    {
        if (bits)
        {
            unsigned rest = bits & (bits - 1);
            int i = __builtin_ctz(bits);
            unions[bits] = unions[rest];
            for (int c : rows[i]) unions[bits] |= 1u << c;
        }
        if ((unions[bits] & required) == required)
            best = min(best, __builtin_popcount(bits));
    }
    return best > m ? -1 : best;
}

void restored(const MinimumCover &d, const vector<MinimumCover::Node> &a,
              const vector<int> &s)
{
    require(d.s == s && d.a.size() == a.size() && d.path.empty());
    for (size_t i = 0; i < a.size(); i++)
        require(d.a[i].l == a[i].l && d.a[i].r == a[i].r &&
                d.a[i].u == a[i].u && d.a[i].d == a[i].d &&
                d.a[i].c == a[i].c && d.a[i].row == a[i].row);
}

void check(int m, const vector<vector<int>> &rows, int want = -2)
{
    cases++;
    if (want == -2) want = brute(m, rows, (1u << m) - 1);
    auto input = rows;
    MinimumCover d(m, rows);
    auto a = d.a;
    auto s = d.s;
    auto inspect = [&](MinimumCover &x)
    {
        if (want >= 0) require(x.lower_bound() <= want);
        auto answer = x.solve();
        require(bool(answer) == (want >= 0));
        if (answer)
        {
            require(int(answer->size()) == want);
            vector<int> covered(m), used(rows.size());
            for (int i : *answer)
            {
                require(0 <= i && i < int(rows.size()));
                require(!used[i]++ && !rows[i].empty());
                for (int c : rows[i]) covered[c]++;
            }
            for (int x : covered) require(x >= 1);
        }
        restored(x, a, s);
    };
    auto fresh = d;
    inspect(fresh);
    inspect(d);
    inspect(d);
    auto copy = d;
    inspect(copy);
    require(rows == input);
    d = MinimumCover(0, {{}, {}});
    require(d.solve() && d.solve()->empty());
    d = MinimumCover(2, {{0}});
    require(!d.solve());
}

void residual_check(int m, const vector<vector<int>> &rows, mt19937 &rng)
{
    MinimumCover d(m, rows);
    auto a = d.a;
    auto s = d.s;
    vector<int> order(rows.size()), undo;
    iota(order.begin(), order.end(), 0);
    shuffle(order.begin(), order.end(), rng);
    for (int row : order)
    {
        unsigned need = 0;
        for (int c = d.a[0].r; c; c = d.a[c].r) need |= 1u << (c - 1);
        int want = brute(m, rows, need);
        if (want >= 0) require(d.lower_bound() <= want);
        residuals++;
        int anchor = -1;
        for (int i = m + 1; i < int(d.a.size()); i++)
            if (d.a[i].row == row && (need >> (d.a[i].c - 1) & 1))
            {
                anchor = i;
                break;
            }
        if (anchor == -1) continue;
        d.remove(anchor);
        undo.push_back(anchor);
        for (int j = d.a[anchor].r; j != anchor; j = d.a[j].r)
        {
            d.remove(j);
            undo.push_back(j);
        }
    }
    for (auto it = undo.rbegin(); it != undo.rend(); it++) d.restore(*it);
    restored(d, a, s);
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
                        vector<vector<int>> rows(n);
                        for (int i = 0; i < n; i++)
                            for (int j = 0; j < m; j++)
                                if (bits >> (i * m + j) & 1) rows[i].push_back(j);
                        check(m, rows);
                    }
        mt19937 rng(5122026);
        for (int t = 0; t < 1200; t++)
        {
            int m = rng() % 10, n = rng() % 12;
            vector<vector<int>> rows(n);
            for (auto &row : rows)
                for (int c = 0; c < m; c++)
                    if (rng() % 3 == 0) row.push_back(c);
            check(m, rows);
            residual_check(m, rows, rng);
            for (auto &row : rows) shuffle(row.begin(), row.end(), rng);
            shuffle(rows.begin(), rows.end(), rng);
            check(m, rows);
        }
        check(3, {{0, 1}, {1, 2}, {0, 2}}, 2);
        check(4, {{0}, {1}, {2}, {3}, {0, 1, 2, 3}}, 1);
        check(2, {{}, {1}, {}, {0}, {1}}, 2);
        vector<vector<int>> identity(500), blocks(500);
        for (int i = 0; i < 500; i++)
        {
            identity[i] = {i};
            for (int j = i / 10 * 10; j < i / 10 * 10 + 10; j++) blocks[i].push_back(j);
        }
        check(500, identity, 500);
        check(500, blocks, 50);
        identity.pop_back();
        check(500, identity, -1);
        check(500, vector<vector<int>>(500), -1);
        vector<vector<int>> overlap(500, vector<int>(500));
        for (auto &row : overlap) iota(row.begin(), row.end(), 0);
        check(500, overlap, 1);
        cout << "PASS " << cases << " cases " << residuals << " residuals " << checks << " checks\n";
    }
    catch (const runtime_error &)
    {
        cout << "ORACLE_REJECT\n";
    }
}
