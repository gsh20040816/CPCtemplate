int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, m;
    cin >> n >> m;
    using H = pheap<pair<int, int>>;
    array<H, 2> q;
    vector<array<H::point_iterator, 2>> h;
    h.reserve(n + m);
    auto add = [&](int x)
    {
        int id = h.size();
        h.push_back({q[0].push({-x, id}), q[1].push({x, id})});
    };
    for (int i = 0; i < n; i++)
    {
        int x;
        cin >> x;
        add(x);
    }
    while (m--)
    {
        int t;
        cin >> t;
        if (t == 0)
        {
            int x;
            cin >> x;
            add(x);
        }
        else
        {
            int k = t - 1;
            auto [x, id] = q[k].top();
            cout << (k ? x : -x) << '\n';
            q[k ^ 1].erase(h[id][k ^ 1]);
            q[k].pop();
        }
    }
}
