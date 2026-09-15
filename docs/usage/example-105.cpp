int main()
{
    using Z = ModInt<469762049>;
    int t;
    cin >> t;
    while (t--)
    {
        long long n;
        int a, b;
        cin >> n >> a >> b;
        Min25<469762049> sieve(n);
        auto power = [&](long long p, int e, long long pe)
        {
            return Z(a) * e + Z(b) * p;
        };
        cout << sieve.sum({a, b, 0}, power).v << '\n';
    }
}
