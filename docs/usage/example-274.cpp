int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, q;
    cin >> n >> q;
    vector<KDMin::Item> p(n);
    for (auto &v : p) cin >> v.p[0] >> v.p[1] >> v.key;
    KDMin kd(p);
    while (q--)
    {
        int op;
        cin >> op;
        if (op == 1)
        {
            int id;
            cin >> id;
            kd.erase(id);
        }
        else
        {
            KDMin::Point low, high;
            cin >> low[0] >> low[1] >> high[0] >> high[1];
            cout << kd.query(low, high) << '\n';
        }
    }
}
