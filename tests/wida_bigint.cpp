#include <bits/stdc++.h>
using namespace std;
#include "fixtures/wida_bigint/main.cpp"

static string show(bigint x)
{
    ostringstream out;
    out << x;
    return out.str();
}

int main(int argc, char **argv)
{
    string mode = argc > 1 ? argv[1] : "ok";
    if (mode == "min") {
        bigint x = LLONG_MIN;
        cout << show(x) << '\n';
        return 0;
    }
    bigint a("123456789012345678901234567890");
    bigint b("987654321098765432109876543210");
    cout << show(a + b) << '\n';
    cout << show(a - b) << '\n';
    cout << show(a * b) << '\n';
    cout << show(a / b) << '\n';
    cout << show(a % b) << '\n';
    cout << show(a * 7) << '\n';
    cout << show(a / 7) << '\n';
    cout << (a % 7) << '\n';
    cout << show(gcd(bigint(12), bigint(18))) << '\n';
    cout << show(lcm(bigint(12), bigint(18))) << '\n';
    cout << (a < b) << (a == a) << (bigint(0) == bigint("0")) << '\n';
    cout << show(-bigint(0)) << ' ' << show(bigint("-0")) << '\n';
    cout << show(bigint(12) * -3) << '\n';
    cout << show(bigint(12) / -5) << '\n';
    cout << (bigint(12) % -5) << '\n';
    cout << show(bigint(-12) / 5) << ' ' << (bigint(-12) % 5) << '\n';
}
