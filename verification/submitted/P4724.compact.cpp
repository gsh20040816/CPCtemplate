#include <bits/stdc++.h>
#include <cassert>
using namespace std;

// BEGIN Hull3D
template <class T = long double>
struct Hull3D
{
    static_assert(is_same_v<T, long long> || is_same_v<T, long double>);
    using W = conditional_t<is_same_v<T, long long>, __int128, long double>;
    struct Point
    {
        T x, y, z;
    };
    vector<Point> p;
    vector<int> id, boundary;
    vector<array<int, 3>> faces;
    int dimension = -1;

    static array<W, 3> normal(Point a, Point b, Point c)
    {
        W x = W(b.x) - a.x;
        W y = W(b.y) - a.y;
        W z = W(b.z) - a.z;
        W u = W(c.x) - a.x;
        W v = W(c.y) - a.y;
        W w = W(c.z) - a.z;
        return {y * w - z * v, z * u - x * w, x * v - y * u};
    }
    static W orient(Point a, Point b, Point c, Point d)
    {
        auto v = normal(a, b, c);
        return v[0] * (W(d.x) - a.x) + v[1] * (W(d.y) - a.y) +
               v[2] * (W(d.z) - a.z);
    }
    // Exact signs for represented floating inputs; nearest rounding, no fast-math.
    // Products and residuals must neither overflow nor underflow.
    using Expansion = vector<long double>;
    static void grow(Expansion &a, long double q)
    {
        Expansion out;
        for (long double x : a)
        {
            long double s = q + x;
            long double v = s - q;
            long double error = (q - (s - v)) + (x - v);
            if (error != 0) out.push_back(error);
            q = s;
        }
        if (q != 0) out.push_back(q);
        a.swap(out);
    }
    static Expansion difference(long double a, long double b)
    {
        Expansion result{a};
        grow(result, -b);
        return result;
    }
    static Expansion product(const Expansion &a, const Expansion &b)
    {
        Expansion result;
        for (long double x : a)
            for (long double y : b)
            {
                long double value = x * y;
                grow(result, fmal(x, y, -value));
                grow(result, value);
            }
        return result;
    }
    static int expansion_sign(const Expansion &a)
    {
        if (a.empty()) return 0;
        return a.back() > 0 ? 1 : -1;
    }
    static int turn_sign(T x, T y, T u, T v, T s, T t)
    {
        W a = W(u) - x;
        W b = W(v) - y;
        W c = W(s) - x;
        W d = W(t) - y;
        W value = a * d - b * c;
        if constexpr (is_same_v<T, long long>)
            return (value > 0) - (value < 0);
        else
        {
            long double bound = 32 * numeric_limits<long double>::epsilon() *
                                (abs(a * d) + abs(b * c));
            if (abs(value) > bound) return value > 0 ? 1 : -1;
            auto result = product(difference(u, x), difference(t, y));
            auto subtract = product(difference(v, y), difference(s, x));
            for (long double z : subtract) grow(result, -z);
            return expansion_sign(result);
        }
    }
    static array<int, 3> normal_sign(Point a, Point b, Point c)
    {
        return {turn_sign(a.y, a.z, b.y, b.z, c.y, c.z),
                turn_sign(a.z, a.x, b.z, b.x, c.z, c.x),
                turn_sign(a.x, a.y, b.x, b.y, c.x, c.y)};
    }
    static int orient_sign(Point a, Point b, Point c, Point d)
    {
        W value = orient(a, b, c, d);
        if constexpr (is_same_v<T, long long>)
            return (value > 0) - (value < 0);
        else
        {
            array<long double, 3> x{b.x - a.x, b.y - a.y, b.z - a.z};
            array<long double, 3> y{c.x - a.x, c.y - a.y, c.z - a.z};
            array<long double, 3> z{d.x - a.x, d.y - a.y, d.z - a.z};
            long double permanent = 0;
            for (int i = 0; i < 3; i++)
            {
                int j = (i + 1) % 3;
                int k = (i + 2) % 3;
                permanent += (abs(x[j] * y[k]) + abs(x[k] * y[j])) * abs(z[i]);
            }
            long double bound = 128 * numeric_limits<long double>::epsilon() * permanent;
            if (abs(value) > bound) return value > 0 ? 1 : -1;
            array<Expansion, 3> ex{difference(b.x, a.x), difference(b.y, a.y), difference(b.z, a.z)};
            array<Expansion, 3> ey{difference(c.x, a.x), difference(c.y, a.y), difference(c.z, a.z)};
            array<Expansion, 3> ez{difference(d.x, a.x), difference(d.y, a.y), difference(d.z, a.z)};
            Expansion result;
            for (int i = 0; i < 3; i++)
            {
                int j = (i + 1) % 3;
                int k = (i + 2) % 3;
                auto positive = product(product(ex[j], ey[k]), ez[i]);
                auto negative = product(product(ex[k], ey[j]), ez[i]);
                for (long double v : positive) grow(result, v);
                for (long double v : negative) grow(result, -v);
            }
            return expansion_sign(result);
        }
    }
    explicit Hull3D(const vector<Point> &input)
    {
        vector<int> order(input.size());
        iota(order.begin(), order.end(), 0);
        for (auto v : input)
        {
            if constexpr (is_same_v<T, long long>)
                assert(-1000000000 <= v.x && v.x <= 1000000000 &&
                       -1000000000 <= v.y && v.y <= 1000000000 &&
                       -1000000000 <= v.z && v.z <= 1000000000);
            else assert(isfinite(v.x) && isfinite(v.y) && isfinite(v.z));
        }
        auto key = [](Point v)
        {
            return make_tuple(v.x, v.y, v.z);
        };
        sort(order.begin(), order.end(), [&](int a, int b)
        {
            return make_tuple(input[a].x, input[a].y, input[a].z, a) <
                   make_tuple(input[b].x, input[b].y, input[b].z, b);
        });
        for (int i : order)
            if (p.empty() || key(input[i]) != key(p.back()))
            {
                p.push_back(input[i]);
                id.push_back(i);
            }
        int n = p.size();
        if (n == 0) return;
        dimension = 0;
        boundary = {0};
        if (n == 1) return;
        dimension = 1;
        boundary = {0, n - 1};
        int c = 2;
        while (c < n && normal_sign(p[0], p[1], p[c]) == array<int, 3>{}) c++;
        if (c == n) return;
        auto axis = normal_sign(p[0], p[1], p[c]);
        int d = 2;
        while (d < n && orient_sign(p[0], p[1], p[c], p[d]) == 0) d++;
        if (d == n)
        {
            dimension = 2;
            int drop = 0;
            while (axis[drop] == 0) drop++;
            auto project = [&](Point v)
            {
                if (drop == 0) return pair<T, T>{v.y, v.z};
                if (drop == 1) return pair<T, T>{v.x, v.z};
                return pair<T, T>{v.x, v.y};
            };
            auto turn = [&](int a, int b, int c)
            {
                auto [x, y] = project(p[a]);
                auto [u, v] = project(p[b]);
                auto [s, t] = project(p[c]);
                return turn_sign(x, y, u, v, s, t);
            };
            order.resize(n);
            iota(order.begin(), order.end(), 0);
            sort(order.begin(), order.end(), [&](int a, int b)
            {
                return project(p[a]) < project(p[b]);
            });
            boundary.clear();
            for (int pass = 0; pass < 2; pass++)
            {
                int base = boundary.size();
                for (int v : order)
                {
                    while ((int)boundary.size() >= base + 2 &&
                           turn(boundary[boundary.size() - 2], boundary.back(), v) <= 0)
                        boundary.pop_back();
                    boundary.push_back(v);
                }
                boundary.pop_back();
                reverse(order.begin(), order.end());
            }
            for (int i = 1; i + 1 < (int)boundary.size(); i++)
                faces.push_back({boundary[0], boundary[i], boundary[i + 1]});
            return;
        }
        dimension = 3;
        boundary.clear();
        array<int, 4> seed{0, 1, c, d};
        for (int i = 0; i < 4; i++)
        {
            array<int, 3> f{seed[(i + 1) % 4], seed[(i + 2) % 4], seed[(i + 3) % 4]};
            if (orient_sign(p[f[0]], p[f[1]], p[f[2]], p[seed[i]]) > 0)
                swap(f[1], f[2]);
            faces.push_back(f);
        }
        for (int v = 0; v < n; v++)
        {
            if (find(seed.begin(), seed.end(), v) != seed.end()) continue;
            vector<array<int, 3>> keep;
            set<pair<int, int>> horizon;
            for (auto f : faces)
            {
                if (orient_sign(p[f[0]], p[f[1]], p[f[2]], p[v]) <= 0)
                {
                    keep.push_back(f);
                    continue;
                }
                for (int k = 0; k < 3; k++)
                {
                    int a = f[k];
                    int b = f[(k + 1) % 3];
                    if (!horizon.erase({b, a})) horizon.insert({a, b});
                }
            }
            for (auto [a, b] : horizon) keep.push_back({a, b, v});
            faces.swap(keep);
        }
    }
    long double area() const
    {
        long double answer = 0;
        for (auto f : faces)
        {
            auto v = normal(p[f[0]], p[f[1]], p[f[2]]);
            answer += hypotl(hypotl((long double)v[0], (long double)v[1]),
                             (long double)v[2]) / 2;
        }
        return answer;
    }
    W volume6() const
    {
        W answer = 0;
        if (dimension != 3) return answer;
        for (auto f : faces) answer += orient(p[0], p[f[0]], p[f[1]], p[f[2]]);
        return answer;
    }
};
// END Hull3D


int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n;
    cin >> n;
    vector<Hull3D<>::Point> p(n);
    for (auto &v : p) cin >> v.x >> v.y >> v.z;
    Hull3D hull(p);
    long double area = hull.area();
    if (hull.dimension == 2) area *= 2;
    cout << fixed << setprecision(3) << area << '\n';
}
