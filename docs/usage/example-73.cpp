int main()
{
    std::ios::sync_with_stdio(false);
    std::cin.tie(nullptr);
    int n, m;
    std::cin >> n >> m;
    WeightedMatching graph(n, n);
    while (m--)
    {
        int x, y;
        long long w;
        std::cin >> x >> y >> w;
        graph.add(x, y, w);
    }
    auto answer = graph.solve();
    assert(answer);
    std::cout << (long long)*answer << '\n';
    for (int j = 1; j <= n; j++) std::cout << graph.r[j] << (j == n ? '\n' : ' ');
}
