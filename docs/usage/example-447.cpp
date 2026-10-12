int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    uint32_t mod;
    int tests;
    cin >> mod >> tests;
    Barrett32 reducer(mod);
    while (tests--)
    {
        uint32_t a, b;
        cin >> a >> b;
        cout << reducer.mul(a, b) << '\n';
    }
}
