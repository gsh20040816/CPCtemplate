int main()
{
    int n, m;
    scanf("%d%d", &n, &m);
    vector<long long> w(n + 1);
    for (int i = 1; i <= n; i++) scanf("%lld", &w[i]);
    HLD h(n);
    for (int i = 1; i < n; i++)
    {
        int u, v;
        scanf("%d%d", &u, &v);
        h.add(u, v);
    }
    h.build(1);
    DynamicDP d(h, w);
    while (m--)
    {
        int x;
        long long y;
        scanf("%d%lld", &x, &y);
        d.set(x, y);
        printf("%lld\n", d.answer());
    }
}
