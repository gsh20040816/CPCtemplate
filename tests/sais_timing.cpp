#include "../src/compact/sais.hpp"
#include "../src/compact/string.hpp"
#include <chrono>
#include <iostream>
#include <string>
using std::chrono::duration;
using std::chrono::steady_clock;

static double once_sais(const string &s)
{
    auto t = steady_clock::now();
    SAIS a(s);
    auto ms = duration<double, std::milli>(steady_clock::now() - t).count();
    volatile int sink = a.sa.empty() ? 0 : a.sa[0];
    (void)sink;
    return ms;
}

static double once_doubling(const string &s)
{
    auto t = steady_clock::now();
    SuffixArray a(s);
    auto ms = duration<double, std::milli>(steady_clock::now() - t).count();
    volatile int sink = a.sa.empty() ? 0 : a.sa[0];
    (void)sink;
    return ms;
}

static void check(const string &name, const string &s)
{
    SAIS a(s);
    SuffixArray b(s);
    if (a.sa != b.sa || a.lcp != b.lcp) {
        cout << name << " mismatch\n";
        return;
    }
    double sais[3], dbl[3];
    for (int i = 0; i < 3; i++) {
        sais[i] = once_sais(s);
        dbl[i] = once_doubling(s);
    }
    auto med = [](double x[3]) {
        if (x[0] > x[1]) std::swap(x[0], x[1]);
        if (x[1] > x[2]) std::swap(x[1], x[2]);
        if (x[0] > x[1]) std::swap(x[0], x[1]);
        return x[1];
    };
    cout << name << ' ' << s.size() << ' ' << med(sais) << ' ' << med(dbl) << '\n';
}

int main()
{
    const int n = 400000;
    string rnd(n, 'a'), per(n, 'a'), run(n, 'a');
    for (int i = 0; i < n; i++) rnd[i] = char('a' + (i * 37 + 11) % 26);
    for (int i = 0; i < n; i++) per[i] = char('a' + (i % 2));
    check("random26", rnd);
    check("alternating", per);
    check("identical", run);
}
