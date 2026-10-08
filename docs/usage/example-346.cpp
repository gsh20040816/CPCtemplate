int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, m, mod;
    while (cin >> n >> m >> mod)
    {
        vector<int> a(n), b(m);
        for (int &x : a)
            cin >> x;
        for (int &x : b)
            cin >> x;
        auto c = convolution_mod(a, b, mod);
        for (int x : c)
            cout << x << ' ';
        cout << '\n';
    }
    return 0;
}
