int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n;
    cin >> n;
    OrderedTreap g;
    while (n--)
    {
        int op;
        long long x;
        cin >> op >> x;
        if (op == 1)
            g.insert(x);
        else if (op == 2)
            g.erase(x);
        else if (op == 3)
            cout << g.rank(x) << '\n';
        else if (op == 4)
            cout << g.kth(x) << '\n';
        else if (op == 5)
            cout << *g.prev(x) << '\n';
        else
            cout << *g.next(x) << '\n';
    }
}
