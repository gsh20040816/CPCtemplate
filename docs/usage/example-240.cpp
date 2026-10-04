int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, m;
    cin >> n >> m;
    vector<IntegerPlane::Point> p(n);
    for (auto &v : p) cin >> v.x >> v.y;
    while (m--)
    {
        IntegerPlane::Point q;
        cin >> q.x >> q.y;
        auto ans = convex_tangents_i64(p, q);
        if (ans)
            cout << ans->first << ' ' << ans->second << '\n';
        else
            cout << "-1 -1\n";
    }
}
