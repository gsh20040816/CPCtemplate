int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, mod, l, r;
    cin >> n >> mod >> l >> r;
    CompositeBinomial comb(n, mod);
    auto coefficient = [&](int h)
    {
        if (h > n)
            return 0LL;
        long long answer = 0;
        for (int down = 0; down <= (n - h) / 2; down++)
        {
            long long ways = comb.choose(n, down);
            ways = ways * comb.choose(n - down, down + h) % mod;
            answer = (answer + ways) % mod;
        }
        return answer;
    };
    long long answer = coefficient(l) + coefficient(l + 1);
    answer -= coefficient(r + 1) + coefficient(r + 2);
    answer = (answer % mod + mod) % mod;
    cout << answer << '\n';
}
