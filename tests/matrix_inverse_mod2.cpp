#include "../src/compact/matrix_inverse_mod2.hpp"

void check(const vector<string> &a, bool invertible)
{
    auto b = matrix_inverse_mod2(a);
    assert(bool(b) == invertible);
    if (!b) return;
    int n = a.size();
    for (int i = 0; i < n; i++)
        for (int j = 0; j < n; j++)
        {
            int left = 0, right = 0;
            for (int k = 0; k < n; k++)
            {
                left ^= (a[i][k] - '0') & ((*b)[k][j] - '0');
                right ^= ((*b)[i][k] - '0') & (a[k][j] - '0');
            }
            assert(left == (i == j) && right == (i == j));
        }
}

int main()
{
    check({}, true);
    for (int mask = 0; mask < 65536; mask++)
    {
        vector<string> a(4, string(4, '0'));
        for (int i = 0; i < 16; i++) a[i / 4][i % 4] += (mask >> i) & 1;
        bool invertible = true;
        for (int x = 1; x < 16; x++)
        {
            int out = 0;
            for (int i = 0; i < 4; i++)
                out |= (__builtin_parity(((mask >> (4 * i)) & 15) & x) << i);
            if (!out) invertible = false;
        }
        check(a, invertible);
    }
    mt19937 rng(896);
    for (int n : {1, 2, 31, 32, 33, 63, 64, 65, 127, 128, 129})
    {
        vector<string> a(n, string(n, '0'));
        for (int i = 0; i < n; i++) a[i][i] = '1';
        for (int step = 0; step < 20 * n; step++)
        {
            int u = rng() % n, v = rng() % n;
            if (u == v) continue;
            for (int j = 0; j < n; j++) a[u][j] = '0' + (a[u][j] != a[v][j]);
            swap(a[u], a[v]);
        }
        check(a, true);
        a[0] = n == 1 ? "0" : a[1];
        check(a, false);
    }
    cout << "matrix_inverse_mod2: all 65536 4x4 matrices by nonzero-kernel "
            "enumeration, two-sided scalar certificates, empty and word-boundary sizes "
            "through 129 PASS\n";
}
