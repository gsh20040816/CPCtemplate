#include <algorithm>
#include <cassert>
#include <cmath>
#include <complex>
#include <limits>
#include <vector>
using namespace std;

struct ComplexFFT
{
    using Real = long double;
    using C = complex<Real>;
    static constexpr int max_size = 1 << 22;
    int n;
    vector<C> roots;

    explicit ComplexFFT(int size) : n(size)
    {
        static_assert(numeric_limits<Real>::radix == 2);
        static_assert(numeric_limits<Real>::digits >= 53);
        assert(n > 0 && n <= max_size && (n & (n - 1)) == 0);
        roots.resize(n / 2);
        Real pi = acosl(-1);
        for (int i = 0; i < n / 2; i++)
        {
            Real angle = pi * (2.0L * i / n);
            roots[i] = C(cosl(angle), sinl(angle));
        }
    }

    void transform(vector<C> &a, bool inverse = false) const
    {
        assert(a.size() == (unsigned)n);
        for (int i = 1, j = 0; i < n; i++)
        {
            int bit = n >> 1;
            for (; j & bit; bit >>= 1) j ^= bit;
            j ^= bit;
            if (i < j) swap(a[i], a[j]);
        }
        for (int half = 1; half < n; half *= 2)
        {
            int step = n / (2 * half);
            for (int i = 0; i < n; i += 2 * half)
            {
                for (int j = 0; j < half; j++)
                {
                    C w = roots[j * step];
                    if (inverse) w = conj(w);
                    C u = a[i + j], v = a[i + j + half] * w;
                    a[i + j] = u + v;
                    a[i + j + half] = u - v;
                }
            }
        }
        if (inverse)
            for (auto &x : a) x /= n;
    }
};

#include <iostream>
#include <iomanip>

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int tests;
    cin >> tests;
    while (tests--)
    {
        int n;
        cin >> n;
        vector<int> a(n);
        for (int &v : a) cin >> v;
        int m = *max_element(a.begin(), a.end()), size = 1;
        while (size <= 2 * m) size *= 2;
        ComplexFFT fft(size);
        vector<ComplexFFT::C> f(size);
        for (int v : a) f[v] += 1;
        fft.transform(f);
        for (auto &v : f) v *= v;
        fft.transform(f, true);
        vector<long long> count(size);
        for (int i = 0; i < size; i++) count[i] = llroundl(f[i].real());
        for (int v : a) count[2 * v]--;
        for (auto &v : count) v /= 2;
        for (int i = 1; i < size; i++) count[i] += count[i - 1];
        long long all = 1LL * n * (n - 1) * (n - 2) / 6;
        long long good = all;
        for (int v : a) good -= count[v];
        cout << fixed << setprecision(7) << (long double)good / all << '\n';
    }
}
