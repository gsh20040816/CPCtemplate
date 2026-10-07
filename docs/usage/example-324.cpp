using S = pair<int, int>;

S op(S a, S b)
{
    return {a.first + b.first, a.second + b.second};
}

S e()
{
    return {0, 0};
}

S mapping(bool flip, S a)
{
    if (flip) swap(a.first, a.second);
    return a;
}

bool composition(bool f, bool g)
{
    return f ^ g;
}

bool id()
{
    return false;
}

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int tests;
    cin >> tests;
    for (int tc = 1; tc <= tests; tc++)
    {
        int n;
        cin >> n;
        HLD h(n);
        map<string, int> names;
        for (int u = 1; u <= n; u++)
        {
            string name;
            cin >> name;
            names[name] = u;
        }
        vector<int> u(n), v(n), bit(n), child(n), parity(n + 1);
        for (int i = 1; i < n; i++)
        {
            string a, b;
            cin >> a >> b >> bit[i];
            u[i] = names.at(a);
            v[i] = names.at(b);
            h.add(u[i], v[i]);
        }
        h.build();
        for (int i = 1; i < n; i++)
        {
            child[i] = h.fa[u[i]] == v[i] ? u[i] : v[i];
            parity[child[i]] = bit[i];
        }
        vector<S> values(n);
        for (int i = 1; i <= n; i++)
        {
            int x = h.rk[i];
            if (x != 1) parity[x] ^= parity[h.fa[x]];
            values[i - 1] = {parity[x] == 0, parity[x] == 1};
        }
        lazy_segtree<S, bool, op, e, mapping, composition, id> seg(values);
        int q;
        cin >> q;
        cout << "Case #" << tc << ":\n";
        while (q--)
        {
            string command;
            cin >> command;
            if (command[0] == 'Q')
            {
                auto [zero, one] = seg.all();
                cout << 2LL * zero * one << '\n';
            }
            else
            {
                int edge;
                cin >> edge;
                int x = child[edge];
                int l = h.dfn[x] - 1;
                seg.apply(l, l + h.siz[x], true);
            }
        }
    }
}
