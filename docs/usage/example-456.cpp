int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    XorAffine64 f;
    cin >> f.bias;
    for (auto &x : f.col)
        cin >> x;
    int q;
    cin >> q;
    while (q--)
    {
        unsigned long long x, k;
        cin >> x >> k;
        cout << f.power(k).apply(x) << '\n';
    }
}
