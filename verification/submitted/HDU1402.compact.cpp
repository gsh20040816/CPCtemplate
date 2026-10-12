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


// BEGIN convolution_fft
// IEEE nearest rounding, root error <= 8 * 2^-53; no fast-math.
vector<long long> convolution_fft(const vector<int> &a, const vector<int> &b)
{
    if (a.empty() || b.empty()) return {};
    assert(a.size() + b.size() - 1 <= ComplexFFT::max_size);
    long double ma = 0, mb = 0;
    for (int v : a) ma = max(ma, fabsl((long double)v));
    for (int v : b) mb = max(mb, fabsl((long double)v));
    assert(ma * mb * sqrtl((long double)a.size() * b.size()) <= 2e12L);
    int size = a.size() + b.size() - 1, n = 1;
    while (n < size) n *= 2;
    ComplexFFT fft(n);
    vector<ComplexFFT::C> x(n), y(n);
    for (int i = 0; i < (int)a.size(); i++) x[i] = a[i];
    for (int i = 0; i < (int)b.size(); i++) y[i] = b[i];
    fft.transform(x);
    fft.transform(y);
    for (int i = 0; i < n; i++) x[i] *= y[i];
    fft.transform(x, true);
    vector<long long> result(size);
    for (int i = 0; i < size; i++) result[i] = llroundl(x[i].real());
    return result;
}

// END convolution_fft

#include <iostream>
#include <string>

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    string s, t;
    while (cin >> s >> t)
    {
        bool negative = (s[0] == '-') != (t[0] == '-');
        int x = s[0] == '+' || s[0] == '-';
        int y = t[0] == '+' || t[0] == '-';
        vector<int> a(s.size() - x), b(t.size() - y);
        for (int i = x; i < int(s.size()); i++) a[s.size() - 1 - i] = s[i] - '0';
        for (int i = y; i < int(t.size()); i++) b[t.size() - 1 - i] = t[i] - '0';
        auto c = convolution_fft(a, b);
        c.push_back(0);
        for (int i = 0; i + 1 < int(c.size()); i++)
        {
            c[i + 1] += c[i] / 10;
            c[i] %= 10;
        }
        while (c.size() > 1 && c.back() == 0) c.pop_back();
        if (negative && c.back() != 0) cout << '-';
        for (int i = int(c.size()) - 1; i >= 0; i--) cout << c[i];
        cout << '\n';
    }
}
