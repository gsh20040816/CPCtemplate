int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, mod, tests;
    cin >> n >> mod >> tests;
    CompositeBinomial comb(n, mod);
    while (tests--)
    {
        int a, b;
        cin >> a >> b;
        cout << comb.choose(a, b) << '\n';
    }
}
