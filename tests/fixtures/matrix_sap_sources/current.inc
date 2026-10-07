using Matrix = vector<vector<long long>>;

pair<long long, Matrix> matrix_flow(const Matrix &cap, int s, int t)
{
    int n = (int)cap.size();
    Isap g(n);
    for (int u = 0; u < n; u++)
        for (int v = 0; v < n; v++)
            if (cap[u][v]) g.add(u + 1, v + 1, cap[u][v]);
    long long value = g.flow(s + 1, t + 1);
    Matrix net(n, vector<long long>(n));
    for (int id = 0; id < (int)g.e.size(); id += 2)
    {
        auto a = g.e[id];
        int u = a.from - 1, v = a.to - 1;
        net[u][v] += g.used(id);
        net[v][u] -= g.used(id);
    }
    return {value, net};
}
