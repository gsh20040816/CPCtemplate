int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int q, p;
    unsigned long long n, k;
    cin >> q >> n >> k >> p;
    cout << q_binomial(n, k, q, p) << '\n';
}
