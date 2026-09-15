#include "../src/compact/matrix_inverse.hpp"

template <int P> void check(const vector<vector<ModInt<P>>> &a, bool invertible)
{
    int n = a.size();
    auto b = matrix_inverse<P>(a);
    assert(bool(b) == invertible);
    if (!b) return;
    for (int i = 0; i < n; i++)
        for (int j = 0; j < n; j++)
        {
            __int128 left = 0, right = 0;
            for (int k = 0; k < n; k++)
            {
                left += (__int128)a[i][k].v * (*b)[k][j].v;
                right += (__int128)(*b)[i][k].v * a[k][j].v;
            }
            assert(left % P == (i == j));
            assert(right % P == (i == j));
        }
}

template <int P> void oracle(const vector<vector<ModInt<P>>> &a)
{
    int n = a.size();
    vector<int> p(n);
    iota(p.begin(), p.end(), 0);
    long long det = 0;
    do
    {
        long long term = 1;
        int parity = 0;
        for (int i = 0; i < n; i++)
        {
            term = (__int128)term * a[i][p[i]].v % P;
            for (int j = 0; j < i; j++) parity ^= p[j] > p[i];
        }
        det = (det + (parity ? -term : term)) % P;
    } while (next_permutation(p.begin(), p.end()));
    check<P>(a, det != 0);
}

template <int P> void exhaustive(int n)
{
    int total = 1;
    for (int i = 0; i < n * n; i++) total *= P;
    for (int mask = 0; mask < total; mask++)
    {
        int x = mask;
        vector<vector<ModInt<P>>> a(n, vector<ModInt<P>>(n));
        for (auto &row : a)
            for (auto &v : row)
            {
                v = x % P;
                x /= P;
            }
        oracle<P>(a);
    }
}

int main()
{
    exhaustive<2>(3);
    exhaustive<3>(2);
    oracle<2>({});
    mt19937 rng(4783);
    using Z = ModInt<1000000007>;
    for (int t = 0; t < 1000; t++)
    {
        int n = 1 + rng() % 6;
        vector<vector<Z>> a(n, vector<Z>(n));
        for (auto &row : a)
            for (auto &x : row) x = (long long)rng() - 2147483648LL;
        if (t % 3 == 0 && n > 1) a[0] = a[1];
        oracle<1000000007>(a);
    }
    int n = 400;
    vector<vector<Z>> a(n, vector<Z>(n));
    for (int i = 0; i < n; i++) a[i][i] = 1;
    for (int step = 0; step < 4000; step++)
    {
        int u = rng() % n, v = rng() % n;
        if (u == v) continue;
        Z c = rng();
        for (int j = 0; j < n; j++) a[u][j] = a[u][j] + c * a[v][j];
        swap(a[u], a[v]);
    }
    check<1000000007>(a, true);
    a[0] = a[1];
    check<1000000007>(a, false);
    cout << "matrix_inverse: exhaustive F2 3x3/F3 2x2, empty, 1000 permutation "
            "determinant oracles, left/right certificates, 400x400 dense "
            "invertible/singular PASS\n";
}
