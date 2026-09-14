int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, q;
    cin >> n >> q;

    struct Query
    {
        int type;
        long long a, b;
    };

    vector<Query> ops(n + q);
    vector<long long> xs;
    for (int i = 0; i < n + q; i++)
    {
        auto &o = ops[i];
        o.type = 0;
        if (i >= n) cin >> o.type;
        cin >> o.a;
        if (o.type == 0)
            cin >> o.b;
        else
            xs.push_back(o.a);
    }
    if (xs.empty()) return 0;
    LiChao t(xs);
    int id = 0;
    for (auto o : ops)
        if (o.type == 0)
            t.add({o.a, o.b, id++});
        else
            cout << (long long)t.query(o.a).first << '\n';
}
