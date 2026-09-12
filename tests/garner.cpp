#include "../src/compact/garner.hpp"
#include "../src/classic/garner.hpp"
#include <boost/multiprecision/cpp_int.hpp>
using boost::multiprecision::cpp_int;

cpp_int inverse_big(cpp_int a, cpp_int m)
{
    cpp_int b = m, x = 1, y = 0;
    while (b != 0)
    {
        cpp_int q = a / b;
        cpp_int next = a - q * b;
        a = b;
        b = next;
        next = x - q * y;
        x = y;
        y = next;
    }
    assert(a == 1);
    return (x % m + m) % m;
}

void check(const vector<long long> &b, const vector<long long> &m)
{
    cpp_int product = 1, expected = 0;
    for (auto x : m)
        product *= x;
    // Direct CRT sum, independent of the mixed-radix recurrence.
    for (int i = 0; i < (int)m.size(); i++)
    {
        cpp_int part = product / m[i];
        expected += cpp_int(b[i]) * part * inverse_big(part, cpp_int(m[i]));
    }
    expected = (expected % product + product) % product;
    auto d = garner_digits(b, m);
    assert(d == Garner_Digits(b, m));
    cpp_int reconstructed = 0, place = 1;
    for (int i = 0; i < (int)m.size(); i++)
    {
        assert(0 <= d[i] && d[i] < m[i]);
        reconstructed += place * d[i];
        place *= m[i];
    }
    assert(reconstructed == expected);
    vector<long long> targets = {1, 2, 7, 1000000007, LLONG_MAX};
    if (!m.empty())
        targets.push_back(m.back());
    for (auto target : targets)
    {
        long long want = (expected % target).convert_to<long long>();
        assert(garner(b, m, target) == want);
        assert(Garner(b, m, target) == want);
    }
}

int main()
{
    check({}, {});
    vector<long long> m = {1, 2, 3, 5};
    do
    {
        for (int x = 0; x < 30; x++)
        {
            vector<long long> b;
            for (auto v : m)
                b.push_back(x % v - 4 * v);
            check(b, m);
        }
    } while (next_permutation(m.begin(), m.end()));
    mt19937_64 rng(20260912);
    for (int it = 0; it < 1500; it++)
    {
        vector<long long> b, moduli;
        int n = rng() % 12;
        while ((int)moduli.size() < n)
        {
            long long candidate = rng() % uint64_t(LLONG_MAX) + 1;
            if (it % 2)
                candidate = candidate % 100 + 1;
            bool ok = true;
            for (auto v : moduli)
                ok &= gcd(v, candidate) == 1;
            if (!ok)
                continue;
            moduli.push_back(candidate);
            b.push_back(bit_cast<long long>(rng()));
        }
        check(b, moduli);
    }
    for (auto value : {LLONG_MIN, -1LL, 0LL, 1LL, LLONG_MAX})
        check({value, value, value}, {LLONG_MAX, LLONG_MAX - 1, 1});
    for (vector<long long> bad : {vector<long long>{2, 4}, {7, 7}, {6, 10, 15}})
        for (int style = 0; style < 2; style++)
        {
            bool rejected = false;
            try
            {
                vector<long long> b(bad.size());
                if (style)
                    Garner(b, bad, 1);
                else
                    garner(b, bad, 1);
            }
            catch (const invalid_argument &)
            {
                rejected = true;
            }
            assert(rejected);
        }
    vector<long long> primes, b;
    for (int x = 2; primes.size() < 1000; x++)
    {
        bool prime = true;
        for (int d = 2; d * d <= x; d++)
            if (x % d == 0)
                prime = false;
        if (prime)
        {
            primes.push_back(x);
            b.push_back(bit_cast<long long>(rng()));
        }
    }
    check(b, primes);
    cout << "Garner dual direct cpp_int CRT oracle, mixed-radix reconstruction, signed extremes, noncoprime rejection and 1000 moduli PASS\n";
}
