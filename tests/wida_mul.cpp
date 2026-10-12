#include <bits/stdc++.h>
#include <cassert>
using namespace std;
namespace source
{
#include "fixtures/wida_poly_variants/12D-multiply.cpp"
}
#include "../src/compact/ntt_convolution.hpp"
using N = NttConvolution<998244353>;
constexpr int mod = 998244353;
long long checks = 0;
int normalize(long long x)
{
    x %= mod;
    if (x < 0)
        x += mod;
    return x;
}
void check(bool ok)
{
    if (!ok)
        throw runtime_error("oracle mismatch at " + to_string(checks));
    checks++;
}
vector<int> brute(const vector<int> &a, const vector<int> &b)
{
    vector<int> c(a.size() + b.size() - 1);
    for (int i = 0; i < (int)a.size(); i++)
        for (int j = 0; j < (int)b.size(); j++)
            c[i + j] = normalize(c[i + j] + 1LL * a[i] * b[j]);
    return c;
}
void product(const vector<int> &a, const vector<int> &b)
{
    auto truth = brute(a, b);
    auto got = source::mul(a, b);
    N::Poly x(a.begin(), a.end()), y(b.begin(), b.end());
    auto current = N::multiply(x, y);
    check(got.size() == truth.size() && current.size() == truth.size());
    for (int i = 0; i < (int)truth.size(); i++)
    {
        check(normalize(got[i]) == truth[i]);
        check(current[i].v == truth[i]);
    }
}
int main(int argc, char **argv)
{
    string mode = argc > 1 ? argv[1] : "small";
    if (mode == "singleton")
    {
        vector<int> a{7};
        source::dft(a);
        cout << a[0] << '\n';
        return 0;
    }
    if (mode == "empty")
    {
        auto a = source::mul({}, {1, 2, 3});
        check(a == vector<int>({0, 0}));
        check(N::multiply({}, {1, 2, 3}).empty());
        bool rejected = false;
        try
        {
            source::mul({}, {});
        }
        catch (const length_error &)
        {
            rejected = true;
        }
        check(rejected);
        cout << checks << " empty-input behavior checks PASS\n";
        return 0;
    }
    if (mode == "capacity-source" || mode == "capacity-current")
    {
        int n = 1 << 22;
        vector<int> result;
        if (mode == "capacity-source")
            result = source::mul(vector<int>(n, 1), vector<int>(n + 1, 1));
        else
        {
            auto p = N::multiply(N::Poly(n, 1), N::Poly(n + 1, 1));
            for (auto x : p)
                result.push_back(x.v);
        }
        check(result.size() == (1 << 23));
        for (int i = 0; i < (int)result.size(); i++)
        {
            int truth = min({i + 1, n, 2 * n - i});
            check(normalize(result[i]) == truth);
        }
        cout << checks << " full 2^23 transform coefficients PASS\n";
        return 0;
    }
    check(source::power(31, 1 << 23) == 1);
    check(source::power(31, 1 << 22) == mod - 1);
    mt19937 rng(731523);
    for (int n : {2, 4, 8, 16, 32, 64, 32, 4, 128, 2})
    {
        vector<int> a(n);
        for (int &x : a)
            x = int(rng() % (2 * mod - 1)) - mod + 1;
        vector<int> transformed(n);
        long long root = source::power(31, (1 << 23) / n);
        for (int i = 0; i < n; i++)
        {
            long long step = source::power(root, i), w = 1;
            for (int j = 0; j < n; j++)
            {
                transformed[i] = normalize(transformed[i] + w * a[j]);
                w = w * step % mod;
            }
        }
        auto got = a;
        source::dft(got);
        for (int i = 0; i < n; i++)
            check(normalize(got[i]) == transformed[i]);
        source::idft(got);
        for (int i = 0; i < n; i++)
            check(normalize(got[i]) == normalize(a[i]));
        got = transformed;
        source::idft(got);
        for (int i = 0; i < n; i++)
            check(normalize(got[i]) == normalize(a[i]));
    }
    for (int n : {1, 2, 63, 64, 65, 127, 128, 129, 257})
        for (int m : {1, 2, 63, 64, 65, 127, 128, 129})
            for (int rep = 0; rep < 4; rep++)
            {
                vector<int> a(n), b(m);
                for (int &x : a)
                    x = int(rng() % (2 * mod - 1)) - mod + 1;
                for (int &x : b)
                    x = int(rng() % (2 * mod - 1)) - mod + 1;
                product(a, b);
            }
    product({mod - 1}, {mod - 1});
    product(vector<int>(64, mod - 1), vector<int>(65, mod - 1));
    product(vector<int>(257), vector<int>(129, mod - 1));
    cout << checks << " independent transform/convolution checks PASS\n";
}
