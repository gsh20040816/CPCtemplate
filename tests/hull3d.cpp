#include "../src/compact/hull3d.hpp"

template <class T>
void run(const vector<array<long long, 3>> &input)
{
    using H = Hull3D<T>;
    vector<typename H::Point> points;
    for (auto v : input) points.push_back({T(v[0]), T(v[1]), T(v[2])});
    H h(points);
    cout << h.dimension << ' ' << setprecision(22) << h.area() << ' '
         << (long double)h.volume6() << ' ' << h.p.size() << ' ' << h.faces.size() << '\n';
    for (int i : h.id) cout << i << ' ';
    cout << '\n';
    for (auto f : h.faces) cout << f[0] << ' ' << f[1] << ' ' << f[2] << '\n';
    cout << h.boundary.size();
    for (int i : h.boundary) cout << ' ' << i;
    cout << '\n';
}

int main()
{
    int cases;
    cin >> cases;
    while (cases--)
    {
        int n;
        cin >> n;
        vector<array<long long, 3>> p(n);
        for (auto &v : p) cin >> v[0] >> v[1] >> v[2];
        run<long long>(p);
        run<long double>(p);
    }
}
