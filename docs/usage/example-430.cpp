int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int q;
    cin >> q;
    ShiftSplay tree;
    vector<int> roots(1);
    while (q--)
    {
        int op, r;
        long long x;
        cin >> op >> r >> x;
        if (op == 1)
        {
            cout << tree.insert(roots[r], x) << '\n';
        }
        else if (op == 2)
        {
            auto [left, right] = tree.split(roots[r], x);
            roots[r] = left;
            roots.push_back(right);
            cout << roots.size() - 1 << '\n';
        }
        else if (op == 3)
        {
            tree.add(roots[r], x);
        }
        else if (op == 4)
        {
            int s = x;
            roots[r] = tree.merge(roots[r], roots[s]);
            roots[s] = 0;
        }
        else
        {
            int id = x;
            cout << tree.value(roots[r], id) << '\n';
        }
    }
}
