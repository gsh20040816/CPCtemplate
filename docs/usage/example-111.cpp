int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, m, k;
    cin >> n >> m >> k;
    vector<int> a(n);
    for (int &x : a) cin >> x;
    vector<pair<int, int>> queries(m);
    for (auto &[l, r] : queries)
    {
        cin >> l >> r;
        l--;
    }
    for (long long x : xor_hamming_pairs(a, queries, k)) cout << x << '\n';
}
