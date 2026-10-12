int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int tests;
    cin >> tests;
    while (tests--)
    {
        int n;
        cin >> n;
        vector<int> a(n);
        for (int &v : a) cin >> v;
        int m = *max_element(a.begin(), a.end()), size = 1;
        while (size <= 2 * m) size *= 2;
        ComplexFFT fft(size);
        vector<ComplexFFT::C> f(size);
        for (int v : a) f[v] += 1;
        fft.transform(f);
        for (auto &v : f) v *= v;
        fft.transform(f, true);
        vector<long long> count(size);
        for (int i = 0; i < size; i++) count[i] = llroundl(f[i].real());
        for (int v : a) count[2 * v]--;
        for (auto &v : count) v /= 2;
        for (int i = 1; i < size; i++) count[i] += count[i - 1];
        long long all = 1LL * n * (n - 1) * (n - 2) / 6;
        long long good = all;
        for (int v : a) good -= count[v];
        cout << fixed << setprecision(7) << (long double)good / all << '\n';
    }
}
