int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, q;
    cin >> n >> q;
    GeneralSAM sam;
    vector<int> state(n + 1);
    for (int i = 1; i <= n; i++)
    {
        int parent;
        char c;
        cin >> parent >> c;
        state[i] = sam.add(state[parent], c - 'a');
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
