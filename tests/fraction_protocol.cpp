#include <bits/stdc++.h>
#include <boost/multiprecision/cpp_int.hpp>
#include "../src/compact/fraction.hpp"
using namespace std;
using boost::multiprecision::cpp_int;

template<class T, class W>
void run()
{
    T n, d, m, e;
    string op;
    cin >> n >> d >> op >> m >> e;
    Rational<T, W> a(n, d), b(m, e), c;
    if (op == "+")
        c = a + b;
    else if (op == "-")
        c = a - b;
    else if (op == "*")
        c = a * b;
    else if (op == "/")
        c = a / b;
    else if (op == "self+")
    {
        a += a;
        c = a;
    }
    else if (op == "self-")
    {
        a -= a;
        c = a;
    }
    else if (op == "self*")
    {
        a *= a;
        c = a;
    }
    else if (op == "self/")
    {
        a /= a;
        c = a;
    }
    else if (op == "neg")
        c = -a;
    else if (op == "cmp")
    {
        cout << (a < b) << ' ' << (a > b) << ' ' << (a == b) << ' ';
        cout << (a <= b) << ' ' << (a >= b) << ' ' << (a != b) << '\n';
        return;
    }
    else
        c = a;
    cout << c.num << ' ' << c.den << ' ' << c << '\n';
}

int main()
{
    int q;
    cin >> q;
    while (q--)
    {
        int wide;
        cin >> wide;
        if (wide)
            run<cpp_int, cpp_int>();
        else
            run<long long, __int128_t>();
    }
}
