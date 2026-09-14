int main()
{
    std::ios::sync_with_stdio(false);
    std::cin.tie(nullptr);
    int n, m;
    std::cin >> n >> m;
    std::vector<long long> a(n);
    for (auto &x : a) std::cin >> x;
    TreePathKth tree(a);
    for (int i = 1; i < n; i++)
    {
        int u, v;
        std::cin >> u >> v;
        tree.add(u, v);
    }
    tree.build();
    long long last = 0;
    while (m--)
    {
        long long encoded;
        int v, k;
        std::cin >> encoded >> v >> k;
        int u = encoded ^ last;
        last = tree.kth(u, v, k);
        std::cout << last << '\n';
    }
}
