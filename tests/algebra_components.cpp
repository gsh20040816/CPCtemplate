#include "../src/compact/gauss_mod.hpp"
#include "../src/compact/det_prime.hpp"
#include "../src/compact/mod_matrix.hpp"
#include <iostream>

template <int p> void check()
{
    using G = GaussMod<p>;
    using M = ModMatrix<p>;
    using Z = ModInt<p>;
    using V = vector<vector<Z>>;
    mt19937 rng(98712 + p);
    assert(det_prime<p>({}).v == 1);
    auto empty = G::solve({}, 3);
    assert(empty.consistent && empty.rank == 0 && empty.kernel.size() == 3);
    for (int it = 0; it < 150; it++)
    {
        int n = rng() % 5, m = rng() % 5;
        V a(m, vector<Z>(n + 1));
        for (auto &r : a) for (auto &x : r) x = rng() % p;
        set<vector<int>> solutions;
        int count = 1;
        for (int j = 0; j < n; j++) count *= p;
        for (int mask = 0; mask < count; mask++)
        {
            int t = mask;
            vector<int> v(n);
            for (int &x : v) x = t % p, t /= p;
            bool valid = true;
            for (auto &r : a)
            {
                int sum = 0;
                for (int j = 0; j < n; j++) sum += r[j].v * v[j];
                valid &= sum % p == r[n].v;
            }
            if (valid) solutions.insert(v);
        }
        auto s = G::solve(a, n);
        assert(s.consistent == !solutions.empty());
        if (s.consistent)
        {
            assert((int)s.kernel.size() == n - s.rank);
            int choices = 1;
            for (auto &v : s.kernel) choices *= p;
            set<vector<int>> generated;
            for (int mask = 0; mask < choices; mask++)
            {
                int t = mask;
                auto v = s.particular;
                for (auto &b : s.kernel)
                {
                    int c = t % p;
                    t /= p;
                    for (int j = 0; j < n; j++) v[j] += b[j] * Z(c);
                }
                vector<int> values;
                for (auto x : v) values.push_back(x.v);
                generated.insert(values);
            }
            assert(generated == solutions && (int)generated.size() == choices);
        }
        n = 1 + rng() % 6;
        V mat(n, vector<Z>(n));
        for (auto &r : mat) for (auto &x : r) x = rng() % p;
        vector<int> order(n);
        iota(order.begin(), order.end(), 0);
        int expected = 0;
        do
        {
            int term = 1, sign = 1;
            for (int i = 0; i < n; i++)
            {
                term = term * mat[i][order[i]].v % p;
                for (int j = 0; j < i; j++) if (order[j] > order[i]) sign = -sign;
            }
            expected = (expected + p + sign * term) % p;
        } while (next_permutation(order.begin(), order.end()));
        assert(det_prime<p>(mat).v == expected);
        auto actual = M::power(mat, 7);
        vector<vector<int>> ref(n, vector<int>(n));
        for (int i = 0; i < n; i++) ref[i][i] = 1;
        for (int step = 0; step < 7; step++)
        {
            vector<vector<int>> next(n, vector<int>(n));
            for (int i = 0; i < n; i++) for (int j = 0; j < n; j++)
                for (int k = 0; k < n; k++) next[i][j] = (next[i][j] + ref[i][k] * mat[k][j].v) % p;
            ref = next;
        }
        for (int i = 0; i < n; i++) for (int j = 0; j < n; j++) assert(actual[i][j].v == ref[i][j]);
    }
}
int main()
{
    check<2>();
    check<3>();
    check<5>();
    using M = ModMatrix<1000>;
    M::Matrix a{{1, 1}, {0, 1}};
    for (auto e : {0ULL, 1ULL, 999ULL, ULLONG_MAX})
    {
        auto r = M::power(a, e);
        assert(r[0][0].v == 1 && r[1][1].v == 1 && r[1][0].v == 0);
        assert(r[0][1].v == e % 1000);
    }
    auto r = M::multiply({{1, 2, 3}, {4, 5, 6}}, {{1}, {2}, {3}});
    assert(r.size() == 2 && r[0][0].v == 14 && r[1][0].v == 32);
    cout << "Separated algebra: exhaustive affine solution sets, permutation determinants, repeated-product matrices and uint64 composite-mod powers PASS\n";
}
