int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, m;
    cin >> n >> m;
    SecondMST mst(n);
    while (m--)
    {
        int u, v;
        long long w;
        cin >> u >> v >> w;
        mst.add(u - 1, v - 1, w);
    }
    auto ans = mst.solve();
    // The problem guarantees a strict second tree and a 64-bit answer.
    assert(ans.connected && ans.next);
    cout << (long long)*ans.next << '\n';
}
