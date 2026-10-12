int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int m;
    cin >> m;
    XorAffine64 f;
    while (m--)
    {
        int shift, operation;
        unsigned long long mask;
        cin >> shift >> operation >> mask;
        if (operation == 0)
            f.bias ^= mask;
        for (int i = 0; i < 64; i++)
        {
            auto bit = rotl(1ULL << i, shift);
            f.col[i] ^= bit & (operation == 0 ? ~mask : mask);
        }
    }
    unsigned long long constant, x, exponent;
    cin >> constant >> x >> exponent;
    f.bias ^= constant;
    cout << f.power(exponent).apply(x) << '\n';
}
