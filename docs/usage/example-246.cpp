int main()
{
    std::ios::sync_with_stdio(false);
    std::cin.tie(nullptr);
    int n, q;
    std::cin >> n >> q;
    using ll = long long;
    std::vector<std::array<ll, 3>> a(n);
    std::vector<std::pair<ll, ll>> p;
    for (auto &[x, y, w] : a)
    {
        std::cin >> x >> y >> w;
        p.push_back({x, y});
    }
    std::vector<std::array<ll, 5>> ops(q);
    for (auto &[op, x, y, r, u] : ops)
    {
        std::cin >> op >> x >> y >> r;
        if (op == 0) p.push_back({x, y});
        else std::cin >> u;
    }
    Fenwick2D tree(p);
    for (auto [x, y, w] : a) tree.add(x, y, w);
    for (auto [op, x, y, r, u] : ops)
    {
        if (op == 0) tree.add(x, y, r);
        else std::cout << tree.sum(x, y, r, u) << '\n';
    }
}
