#include "../src/compact/euler_power.hpp"
#include <boost/multiprecision/cpp_int.hpp>
using boost::multiprecision::cpp_int;
using U = unsigned long long;

void check(U a, const string &b, U m, U phi)
{
    cpp_int exponent = 0;
    for (char c : b) exponent = exponent * 10 + c - '0';
    cpp_int expected = boost::multiprecision::powm(cpp_int(a), exponent, cpp_int(m));
    assert(euler_power(a, b, m, phi) == expected.convert_to<U>());
}

int main()
{
    for (U m = 1; m <= 100; m++)
    {
        U phi = 0;
        for (U x = 1; x <= m; x++) phi += gcd(x, m) == 1;
        for (U a = 0; a <= 50; a++)
        {
            U expected = 1 % m;
            for (int e = 0; e <= 130; e++)
            {
                assert(euler_power(a, to_string(e), m, phi) == expected);
                assert(euler_power(a, "000" + to_string(e), m, phi) == expected);
                expected = expected * a % m;
            }
        }
    }
    mt19937_64 rng(5091);
    vector<pair<U, U>> moduli{{1, 1},
                              {1ULL << 63, 1ULL << 62},
                              {18446744073709551557ULL, 18446744073709551556ULL},
                              {ULLONG_MAX, 9208981628670443520ULL},
                              {1000000007, 1000000006}};
    for (auto [m, phi] : moduli)
    {
        for (U e : {0ULL, 1ULL, phi - 1, phi, phi + 1, ULLONG_MAX})
            for (U a : {0ULL, 1ULL, 2ULL, ULLONG_MAX}) check(a, to_string(e), m, phi);
        check(ULLONG_MAX, (cpp_int(phi) * 2 + 17).convert_to<string>(), m, phi);
        for (int t = 0; t < 30; t++)
        {
            string b;
            for (int i = 0; i < 200; i++) b += char('0' + rng() % 10);
            check(rng(), b, m, phi);
        }
    }
    cout << "euler_power: exhaustive small a/m/e with leading zeroes, independent "
            "repeated multiplication, cpp_int powm over full unsigned64 and 200-digit "
            "exponents, phi threshold and 65-bit reduced exponent PASS\n";
}
