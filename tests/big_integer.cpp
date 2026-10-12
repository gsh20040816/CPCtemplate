#include "../src/compact/big_integer.hpp"

void check(const BigInteger &a)
{
    if (a.sign != 1 && a.sign != -1)
        abort();
    if (a.d.empty() && a.sign != 1)
        abort();
    if (!a.d.empty() && a.d.back() == 0)
        abort();
    for (int x : a.d)
        if (x < 0 || x >= a.base)
            abort();
}

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    string op, s, t;
    while (cin >> op >> s)
    {
        BigInteger a(s);
        check(a);
        BigInteger copied = a;
        copied = copied;
        if (copied.str() != a.str())
            abort();
        BigInteger result;
        if (op == "parse")
            result = a;
        else if (op == "int")
            result = BigInteger(stoll(s));
        else if (op == "neg")
            result = -a;
        else if (op == "pow")
        {
            unsigned int e;
            cin >> e;
            result = a.pow(e);
        }
        else if (op == "div")
        {
            int b;
            cin >> b;
            auto [q, r] = a.divmod(b);
            check(q);
            cout << q.str() << ' ' << r << '\n';
            continue;
        }
        else
        {
            cin >> t;
            BigInteger b(t);
            check(b);
            if (op == "cmp")
            {
                cout << a.cmp(b) << ' ' << a.abs_cmp(b) << '\n';
                continue;
            }
            if (op == "add")
                result = a + b;
            else if (op == "sub")
                result = a - b;
            else if (op == "mul")
                result = a * b;
            else
                result = (a - b) * (a + b) + b * b;
            if (a.str() != BigInteger(s).str() || b.str() != BigInteger(t).str())
                abort();
        }
        check(result);
        cout << result.str() << '\n';
    }
}
