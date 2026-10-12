int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n;
    cin >> n;
    SequenceMaxTreap tree;
    int root = 0;
    for (int i = 0; i < n; i++)
    {
        int importance, limit;
        cin >> importance >> limit;
        int barrier = tree.last_greater(root, importance);
        int pos = max(i - limit, barrier + 1);
        tree.insert(root, pos, importance);
    }
    auto order = tree.ids(root);
    for (int i = 0; i < n; i++)
        cout << order[i] << (i + 1 == n ? '\n' : ' ');
}
