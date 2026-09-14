int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    long long n;
    cin >> n;
    DuJiao d(min(n, 2000000LL));
    cout << (long long)(d.totient_sum(n) % 998244353) << '\n';
}
