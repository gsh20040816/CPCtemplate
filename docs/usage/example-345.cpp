int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, m, mod;
    cin >> n >> m >> mod;
    vector<int> a(n + 1), b(m + 1);
    for (int &x : a)
        cin >> x;
    for (int &x : b)
        cin >> x;
    auto c = convolution_mod(a, b, mod);
    for (int x : c)
        cout << x << ' ';
    cout << '\n';
    return 0;
}
