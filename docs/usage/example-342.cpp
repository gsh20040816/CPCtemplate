int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, alphabet;
    cin >> n >> alphabet;
    vector<int> s(n);
    for (int &c : s)
        cin >> c;
    DC3 d(s, alphabet);
    for (int x : d.sa)
        cout << x << ' ';
    cout << '\n';
    for (int x : d.rk)
        cout << x << ' ';
    cout << '\n';
    for (int x : d.lcp)
        cout << x << ' ';
    cout << '\n';
    return 0;
}
