int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, size;
    long long colors, mod;
    cin >> n >> size >> colors >> mod;
    BurnsideAverage avg(size, mod);
    for (int i = 0; i < size; i++)
    {
        vector<int> p(n);
        for (int &x : p) cin >> x;
        avg.add(avg.power(colors, permutation_cycles(p).size()));
    }
    cout << avg.result() << '\n';
}
