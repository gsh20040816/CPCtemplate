int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, mod, strict;
    cin >> n >> mod >> strict;
    vector<Chain3D::Point> p(n);
    for (auto &v : p) cin >> v[0] >> v[1] >> v[2];
    Chain3D chain(p, mod, strict);
    cout << chain.length << ' ' << chain.count << '\n';
    for (int id : chain.path()) cout << id << ' ';
    cout << '\n';
    for (int i = 0; i < n; i++)
    {
        cout << chain.len[i] << ' ' << chain.ways[i] << ' ' << chain.parent[i] << '\n';
    }
}
