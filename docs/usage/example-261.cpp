int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, q;
    string s;
    cin >> n >> q >> s;
    vector<vector<int>> g(n);
    for (int i = 1; i < n; i++)
    {
        int u, v;
        cin >> u >> v;
        u--;
        v--;
        g[u].push_back(v);
        g[v].push_back(u);
    }
    GeneralSAM sam;
    vector<int> par(n, -1), state(n);
    state[0] = sam.add(0, s[0] - 'a');
    queue<int> todo;
    todo.push(0);
    while (!todo.empty())
    {
        int u = todo.front();
        todo.pop();
        for (int v : g[u])
        {
            if (v == par[u]) continue;
            par[v] = u;
            state[v] = sam.add(state[u], s[v] - 'a');
            todo.push(v);
        }
    }
    sam.build();
    cout << sam.distinct() + 1 << '\n';
    SAMLex index(sam);
    while (q--)
    {
        string alphabet;
        long long k;
        cin >> alphabet >> k;
        if (k == 1) cout << '\n';
        else
        {
            auto ans = index.kth(k - 1, alphabet);
            cout << (ans ? *ans : "-1") << '\n';
        }
    }
}
