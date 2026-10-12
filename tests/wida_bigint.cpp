#include <bits/stdc++.h>
#include <cassert>
using namespace std;
namespace original
{
#include "fixtures/wida_bigint/bigint.cpp"
}
#include "../src/compact/big_integer.hpp"

original::BigInt seeded(const string &s)
{
    original::BigInt x;
    for (int i = 0; i < (int)s.size(); i++)
        x.a[i] = s[s.size() - 1 - i] - '0';
    return x;
}
string print(const original::BigInt &x)
{
    for (int i = 0; i < original::N; i++)
        if (x.a[i] < 0 || x.a[i] > 9)
            throw runtime_error("noncanonical source digits");
    ostringstream out;
    out << x;
    return out.str();
}
int main(int argc, char **argv)
{
    string task = argc > 1 ? argv[1] : "normal";
    if (task == "zero")
    {
        cout << original::BigInt(0) << '\n';
        return 0;
    }
    if (task == "carry")
    {
        auto a = seeded(string(1000, '9'));
        a += original::BigInt(1);
        cout << a << '\n';
        return 0;
    }
    if (task == "multiply")
    {
        original::BigInt a(9);
        a *= INT_MAX;
        cout << a << '\n';
        return 0;
    }
    if (task == "divide")
    {
        auto a = seeded("10000000000");
        a /= INT_MAX;
        cout << a << '\n';
        return 0;
    }
    if (task == "alias")
    {
        original::BigInt a(9);
        a += a;
        BigInteger b(9);
        cout << print(a) << ' ' << (b + b).str() << '\n';
        return 0;
    }
    if (task == "current")
    {
        cout << BigInteger(0).str() << '\n';
        cout << (BigInteger(string(1000, '9')) + BigInteger(1)).str() << '\n';
        cout << (BigInteger(9) * BigInteger(INT_MAX)).str() << '\n';
        auto result = BigInteger("10000000000").divmod(INT_MAX);
        cout << result.first.str() << ' ' << result.second << '\n';
        return 0;
    }
    char op;
    string s;
    while (cin >> op >> s)
    {
        auto a = seeded(s);
        BigInteger b(s);
        if (op == '+')
        {
            string t;
            cin >> t;
            a += seeded(t);
            b = b + BigInteger(t);
        }
        else
        {
            int x;
            cin >> x;
            if (op == '*')
            {
                a *= x;
                b = b * BigInteger(x);
            }
            else
            {
                a /= x;
                b = b.divmod(x).first;
            }
        }
        cout << print(a) << ' ' << b.str() << '\n';
    }
}
