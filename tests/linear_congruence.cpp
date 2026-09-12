#include "../src/compact/linear_congruence.hpp"
#include "../src/classic/linear_congruence.hpp"
#include <boost/multiprecision/cpp_int.hpp>
#include <random>
using boost::multiprecision::cpp_int;

void check(long long a, long long b, long long m, bool brute)
{
    auto result = linear_congruence(a, b, m);
    assert(result == Linear_Congruence(a, b, m));
    long long reduced = a % m;
    if (reduced < 0)
        reduced += m;
    long long g = gcd(reduced, m);
    if (b % g)
    {
        assert(result.first == -1 && result.second == -1);
    }
    else
    {
        auto [x, period] = result;
        assert(period == m / g);
        assert(0 <= x && x < period);
        assert((cpp_int(a) * x + b) % m == 0);
        for (int t : {-7, -1, 0, 1, 9})
            assert((cpp_int(a) * (cpp_int(x) + cpp_int(period) * t) + b) % m == 0);
    }
    if (brute)
    {
        vector<long long> solutions;
        for (long long x = 0; x < m; x++)
            if ((__int128_t(a) * x + b) % m == 0)
                solutions.push_back(x);
        if (solutions.empty())
            assert(result.first == -1);
        else
        {
            assert(result.first == solutions[0]);
            assert((long long)solutions.size() == g);
            for (int i = 0; i < (int)solutions.size(); i++)
                assert(solutions[i] == result.first + i * result.second);
        }
    }
}

int main()
{
    for (int m = 1; m <= 50; m++)
        for (int a = -2 * m; a <= 2 * m; a++)
            for (int b = -2 * m; b <= 2 * m; b++)
                check(a, b, m, true);
    vector<long long> edge = {LLONG_MIN, LLONG_MIN + 1, -1, 0, 1, LLONG_MAX - 1, LLONG_MAX};
    for (auto a : edge)
        for (auto b : edge)
            for (long long m : {1LL, 2LL, 3LL, 1LL << 62, LLONG_MAX - 1, LLONG_MAX})
                check(a, b, m, m <= 3);
    mt19937_64 rng(2115);
    for (int i = 0; i < 10000; i++)
        check(bit_cast<long long>(rng()), bit_cast<long long>(rng()), 1 + rng() % LLONG_MAX, false);
    cout << "Linear congruence dual exhaustive residue sets, minimal solution/period, modulus one and signed int64 cpp_int certificates PASS\n";
}
