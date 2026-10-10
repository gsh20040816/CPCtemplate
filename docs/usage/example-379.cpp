int main()
{
    int n, m;
    cin >> n >> m;
    vector<pair<int, int>> edges(m);
    for (auto &[u, v] : edges)
        cin >> u >> v;
    cout << count_four_cycles(n, edges) << '\n';
}
