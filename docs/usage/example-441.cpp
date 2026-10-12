int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    Rational<> sum;
    long long num, den;
    char slash;
    while (cin >> num >> slash >> den)
        sum += Rational<>(num, den);
    cout << sum << '\n';
}
