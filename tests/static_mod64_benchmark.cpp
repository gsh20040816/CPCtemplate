#include "../src/compact/static_mod64.hpp"
constexpr uint64_t mod = 18446744073709551557ULL;
__attribute__((noinline)) uint64_t ordinary(int n)
{
    uint64_t x = 17;
    for (int i = 0; i < n; i++)
        x = (__uint128_t(x) * 1234567 + 1) % mod;
    return x;
}
__attribute__((noinline)) uint64_t wrapped(int n)
{
    using Z = StaticMod64<mod>;
    Z x(17), b(1234567), one(1);
    for (int i = 0; i < n; i++)
    {
        x *= b;
        x += one;
    }
    return x.v;
}
int main(int argc, char **argv)
{
    int n = stoi(argv[1]);
    auto start = chrono::steady_clock::now();
    auto value = string(argv[2]) == "ordinary" ? ordinary(n) : wrapped(n);
    double seconds = chrono::duration<double>(chrono::steady_clock::now() - start).count();
    cout << value << ' ' << seconds << '\n';
}
