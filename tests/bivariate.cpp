#include "../src/compact/bivariate_inverse.hpp"
#include <cstdlib>
using F = BivariateInverse;
using M = F::Matrix;
constexpr long long P = 998244353;
long long checks = 0;
void check(bool ok)
{
    if (!ok)
        abort();
    checks++;
}
long long power(long long a, long long e, int p)
{
    long long b = 1;
    while (e)
    {
        if (e & 1)
            b = b * a % p;
        a = a * a % p;
        e >>= 1;
    }
    return b;
}

template <int p, int g> void ntt_checks()
{
    using N = Ntt2D<p, g>;
    mt19937 rng(p);
    for (int n : {1, 2, 4, 8, 1, 4})
        for (int m : {1, 2, 4, 8, 2, 1})
        {
            typename N::Matrix a(n, vector<typename N::Z>(m));
            for (auto &row : a)
                for (auto &x : row)
                    x = rng() % p;
            auto original = a;
            vector<vector<long long>> want(n, vector<long long>(m));
            long long x = power(g, (p - 1) / n, p);
            long long y = power(g, (p - 1) / m, p);
            for (int i = 0; i < n; i++)
                for (int j = 0; j < m; j++)
                    for (int u = 0; u < n; u++)
                        for (int v = 0; v < m; v++)
                            want[i][j] = (want[i][j] + original[u][v].v * power(x, i * u, p) % p * power(y, j * v, p)) % p;
            N::transform(a, true);
            long long scale = power(n * m, p - 2, p);
            for (int i = 0; i < n; i++)
                for (int j = 0; j < m; j++)
                    check(a[i][j].v == want[(n - i) % n][(m - j) % m] * scale % p);
            a = original;
            N::transform(a);
            for (int i = 0; i < n; i++)
                for (int j = 0; j < m; j++)
                    check(a[i][j].v == want[i][j]);
        }
    for (int t = 0; t < 100; t++)
    {
        int n = 1 + rng() % 7, m = 1 + rng() % 7;
        int h = 1 + rng() % 7, w = 1 + rng() % 7;
        typename N::Matrix a(n, vector<typename N::Z>(m));
        typename N::Matrix b(h, vector<typename N::Z>(w));
        for (auto &row : a)
            for (auto &x : row)
                x = rng() % p;
        for (auto &row : b)
            for (auto &x : row)
                x = rng() % p;
        vector<vector<long long>> want(n + h - 1, vector<long long>(m + w - 1));
        for (int i = 0; i < n; i++)
            for (int j = 0; j < m; j++)
                for (int u = 0; u < h; u++)
                    for (int v = 0; v < w; v++)
                        want[i + u][j + v] = (want[i + u][j + v] + 1LL * a[i][j].v * b[u][v].v) % p;
        auto got = N::multiply(a, b);
        check(got.size() == want.size());
        for (int i = 0; i < (int)want.size(); i++)
        {
            check(got[i].size() == want[i].size());
            for (int j = 0; j < (int)want[i].size(); j++)
                check(got[i][j].v == want[i][j]);
        }
    }
    check(N::multiply({}, {}).empty());
    check(N::multiply({{}}, {{1}}).empty());
}

int main()
{
    ntt_checks<17, 3>();
    ntt_checks<97, 5>();
    ntt_checks<998244353, 3>();
    mt19937 rng(451);
    for (int t = 0; t < 300; t++)
    {
        int n = 1 + rng() % 9, m = 1 + rng() % 9;
        M a(1 + rng() % 12);
        for (auto &row : a)
        {
            row.resize(rng() % 12);
            for (auto &x : row)
                x = rng() % P;
        }
        if (a[0].empty())
            a[0].resize(1);
        a[0][0] = 1 + rng() % (P - 1);
        vector<vector<long long>> want(n, vector<long long>(m));
        long long inverse = power(a[0][0].v, P - 2, P);
        for (int i = 0; i < n; i++)
            for (int j = 0; j < m; j++)
            {
                long long sum = 0;
                for (int u = 0; u <= i && u < (int)a.size(); u++)
                    for (int v = 0; v <= j && v < (int)a[u].size(); v++)
                        if (u != 0 || v != 0)
                            sum = (sum + a[u][v].v * want[i - u][j - v]) % P;
                want[i][j] = ((i == 0 && j == 0) ? inverse : (P - sum) * inverse % P);
            }
        auto got = F::inverse(a, n, m);
        check((int)got.size() == n);
        for (int i = 0; i < n; i++)
        {
            check((int)got[i].size() == m);
            for (int j = 0; j < m; j++)
                check(got[i][j].v == want[i][j]);
        }
    }
    auto r = F::inverse({{1}}, 257, 129);
    for (int i = 0; i < 257; i++)
        for (int j = 0; j < 129; j++)
            check(r[i][j].v == (i == 0 && j == 0));
    auto c = F::multiply(M(129, vector<F::Z>(65, 1)), M(129, vector<F::Z>(65, 1)));
    for (int i = 0; i < 257; i++)
        for (int j = 0; j < 129; j++)
            check(c[i][j].v == min(i + 1, 257 - i) * min(j + 1, 129 - j));
    cout << checks << " independent 2D DFT/convolution/inverse checks PASS\n";
}
