int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, m, k;
    cin >> n >> m >> k;
    KShortestWalks solver(n);
    for (int i = 0; i < m; i++)
    {
        int u, v;
        long long w;
        cin >> u >> v >> w;
        solver.add(u, v, w);
    }
    auto answer = solver.run(n, 1, k);
    for (int i = 0; i < k; i++)
    {
        cout << (i < int(answer.size()) ? answer[i] : -1) << '\n';
    }
}
