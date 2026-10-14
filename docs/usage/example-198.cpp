int read()
{
    int c = getchar_unlocked();
    while (c < '0' || c > '9')
    {
        if (c == EOF) return 0;
        c = getchar_unlocked();
    }
    int value = 0;
    while ('0' <= c && c <= '9')
    {
        value = value * 10 + c - '0';
        c = getchar_unlocked();
    }
    return value;
}

int main()
{
    int n = read(), p = read(), k = read();
    mint<>::set_mod(p);
    vector<mint<>> a(n);
    for (auto &x : a) x = read();
    // Batch inverse: one inversion of the prefix product.
    vector<mint<>> prefix(n + 1, 1);
    for (int i = 0; i < n; i++) prefix[i + 1] = prefix[i] * a[i];
    auto total = prefix[n].try_inv();
    if (!total) return 1;
    mint<> suffix = *total, answer = 0;
    vector<mint<>> inverse(n);
    for (int i = n - 1; i >= 0; i--)
    {
        inverse[i] = suffix * prefix[i];
        suffix *= a[i];
    }
    mint<> weight = 1;
    for (auto x : inverse)
    {
        weight *= mint<>(k);
        answer += weight * x;
    }
    printf("%d\n", answer.v);
    return 0;
}
