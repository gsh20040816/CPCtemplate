int main()
{
    string s, t;
    int d;
    unsigned int e;
    cin >> s >> t >> d >> e;
    BigInteger a(s), b(t);
    cout << (a + b).str() << '\n';
    cout << (a - b).str() << '\n';
    cout << (a * b).str() << '\n';
    cout << a.cmp(b) << '\n';
    auto [q, r] = a.divmod(d);
    cout << q.str() << ' ' << r << '\n';
    cout << a.pow(e).str() << '\n';
}
