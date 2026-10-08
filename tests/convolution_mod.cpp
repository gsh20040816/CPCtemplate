#include "../src/compact/convolution_mod.hpp"

long long cases = 0;

void require(bool ok)
{
    if (!ok)
    {
        cerr << "wrong convolution at case " << cases << '\n';
        exit(1);
    }
}

vector<int> brute(const vector<int> &a, const vector<int> &b, int mod)
{
    if (a.empty() || b.empty())
        return {};
    vector<int> c(a.size() + b.size() - 1);
    for (int i = 0; i < (int)a.size(); i++)
        for (int j = 0; j < (int)b.size(); j++)
        {
            __int128 value = (__int128)a[i] * b[j] + c[i + j];
            value %= mod;
            if (value < 0)
                value += mod;
            c[i + j] = value;
        }
    return c;
}

void check(const vector<int> &a, const vector<int> &b, int mod)
{
    auto x = a, y = b;
    auto got = convolution_mod(x, y, mod);
    require(x == a && y == b);
    require(got == brute(a, b, mod));
    cases++;
}

int main()
{
    vector<vector<int>> words(1);
    vector<vector<int>> level(1);
    for (int n = 1; n <= 3; n++)
    {
        vector<vector<int>> next;
        for (auto a : level)
            for (int v : {-2, 0, 1})
            {
                auto b = a;
                b.push_back(v);
                next.push_back(b);
                words.push_back(b);
            }
        level = move(next);
    }
    vector<int> mods = {1, 2, 4, 6, 1000003, 167772161, 469762049,
                       998244353, 1000000007, 1224736769, INT_MAX};
    for (const auto &a : words)
        for (const auto &b : words)
            for (int mod : mods)
                check(a, b, mod);
    mt19937 rng(20261008);
    vector<int> values = {INT_MIN, INT_MAX, -1, 0, 1, 1000000009};
    for (int rep = 0; rep < 2500; rep++)
    {
        vector<int> a(rng() % 40), b(rng() % 40);
        for (int &v : a)
            v = rep % 2 ? (int)rng() : values[rng() % values.size()];
        for (int &v : b)
            v = rep % 2 ? (int)rng() : values[rng() % values.size()];
        int mod = rep % 3 ? mods[rng() % mods.size()] : 1 + rng() % INT_MAX;
        check(a, b, mod);
    }
    // True nonnegative coefficients far exceed signed64; closed-form overlap counts.
    for (int m : {131071, 131072, 131073})
    {
        int n = 131072, mod = INT_MAX;
        vector<int> a(n, -1), b(m, -1);
        auto c = convolution_mod(move(a), move(b), mod);
        require(c.size() == n + m - 1);
        for (int k = 0; k < (int)c.size(); k++)
        {
            int count = min({k + 1, n, m, n + m - 1 - k});
            require(c[k] == count);
        }
        cases++;
    }
    cout << cases << '\n';
}
