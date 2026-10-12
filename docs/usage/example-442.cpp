int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    using boost::multiprecision::cpp_int;
    using F = Rational<cpp_int, cpp_int>;
    int q;
    cin >> q;
    while (q--)
    {
        cpp_int an, ad, bn, bd;
        char op;
        cin >> an >> ad >> op >> bn >> bd;
        F a(an, ad), b(bn, bd);
        if (op == '+')
            cout << a + b << '\n';
        else if (op == '-')
            cout << a - b << '\n';
        else if (op == '*')
            cout << a * b << '\n';
        else if (op == '/')
            cout << a / b << '\n';
        else
            cout << (a < b ? -1 : a == b ? 0 : 1) << '\n';
    }
}
