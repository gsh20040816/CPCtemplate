int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    unsigned long long a, x, mod;
    cin >> a >> x >> mod;
    cout << power_sum(a, x, mod).second << '\n';
    return 0;
}
