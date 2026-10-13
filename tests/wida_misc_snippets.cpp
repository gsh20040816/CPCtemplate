#include <bits/stdc++.h>
#include <clocale>
using namespace std;
#include "fixtures/wida_misc/03 - 字符调整.cpp"

template <class Check>
int last_true(int lo, int hi, Check check)
{
    while (lo < hi) {
        int m = (lo + hi + 1) / 2;
        if (check(m)) {
            lo = m;
        } else {
            hi = m - 1;
        }
    }
    return lo;
}

template <class Check>
int first_true(int lo, int hi, Check check)
{
    while (lo < hi) {
        int m = (lo + hi) / 2;
        if (check(m)) {
            hi = m;
        } else {
            lo = m + 1;
        }
    }
    return lo;
}

template <class Check>
double real_cut(double lo, double hi, double eps, Check check)
{
    while (hi - lo > std::max(1.0, lo) * eps) {
        double x = (lo + hi) / 2;
        if (check(x)) {
            hi = x;
        } else {
            lo = x;
        }
    }
    return lo;
}

template <class F>
long double ternary_min(F f)
{
    using real = long double;
    constexpr real eps = 1E-7;
    real lo = -1E4, hi = 1E4;
    while (hi - lo > 3 * eps) {
        real x1 = (lo + hi - eps) / 2;
        real x2 = (lo + hi + eps) / 2;
        if (f(x1) > f(x2)) {
            lo = x1;
        } else {
            hi = x2;
        }
    }
    return f((lo + hi) / 2);
}

int main(int argc, char **argv)
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    setlocale(LC_ALL, "C");
    string mode = argc > 1 ? argv[1] : "cases";
    if (mode == "overflow")
    {
        int lo = INT_MAX - 1, hi = INT_MAX;
        cout << (lo + hi + 1) / 2 << '\n';
        return 0;
    }
    string s = "a1c";
    rev(s);
    cout << s << '\n';
    s = "abcd";
    rev(s);
    cout << s << '\n';
    s = "";
    rev(s);
    cout << s.size() << '\n';
    s = "Z";
    rev(s);
    cout << s << '\n';
    cout << get('a') << ' ' << get('z') << ' ' << get('A') << ' ' << get('Z') << ' ' << get('0') << '\n';
    cout << last_true(1, 20, [](int m) { return m <= 7; }) << '\n';
    cout << last_true(1, 20, [](int) { return false; }) << '\n';
    cout << last_true(1, (int)1e9, [](int) { return true; }) << '\n';
    cout << first_true(1, 20, [](int m) { return m >= 5; }) << '\n';
    cout << first_true(1, 20, [](int) { return false; }) << '\n';
    cout << first_true(1, 20, [](int) { return true; }) << '\n';
    cout << setprecision(12) << real_cut(0, 1e12, 1e-9, [](double x) { return x >= 2.5; }) << '\n';
    cout << (double)ternary_min([](long double x) { return (x - 3) * (x - 3); }) << '\n';
    cout << (double)ternary_min([](long double x) { return -x; }) << '\n';
}
