#include "../src/compact/montgomery_modint.hpp"
using Clock = chrono::steady_clock;
constexpr uint32_t mod = 998244353;
__attribute__((noinline)) uint32_t ordinary(int n)
{
    uint64_t x = 17;
    for (int i = 0; i < n; i++)
        x = (x * 1234567 + 1) % mod;
    return x;
}
__attribute__((noinline)) uint32_t montgomery(int n)
{
    using Z = Montgomery<mod>;
    Z x(17), b(1234567), one(1);
    for (int i = 0; i < n; i++)
    {
        x *= b;
        x += one;
    }
    return x.get();
}
int main(int argc, char **argv)
{
    int n = stoi(argv[1]);
    auto start = Clock::now();
    auto result = string(argv[2]) == "ordinary" ? ordinary(n) : montgomery(n);
    double seconds = chrono::duration<double>(Clock::now() - start).count();
    cout << result << ' ' << seconds << '\n';
}
