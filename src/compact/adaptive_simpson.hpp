#pragma once
#include <bits/stdc++.h>
using namespace std;

struct AdaptiveSimpson
{
    using ld = long double;
    struct Result
    {
        ld value, error;
        int evaluations;
        bool met;
    };

    template<class F>
    static Result integrate(F &&f, ld a, ld b, ld eps,
                            int depth = 20, int limit = 100000)
    {
        const ld inf = numeric_limits<ld>::infinity();
        const ld nan = numeric_limits<ld>::quiet_NaN();
        if (!isfinite(a) || !isfinite(b) || !isfinite(eps) || eps <= 0 ||
            depth < 0 || depth > 60 || limit < 0)
            return {nan, inf, 0, false};
        if (a == b) return {0, 0, 0, true};
        if (limit < 3) return {nan, inf, 0, false};
        bool reverse = a > b;
        if (reverse) swap(a, b);
        auto area = [](ld l, ld r, ld u, ld v, ld w)
        {
            return (r - l) / 6 * (u + 4 * v + w);
        };
        ld fa = f(a), fm = f(midpoint(a, b)), fb = f(b);
        int used = 3;
        ld whole = area(a, b, fa, fm, fb);
        if (!isfinite(fa) || !isfinite(fm) || !isfinite(fb) || !isfinite(whole))
            return {nan, inf, used, false};
        auto rec = [&](auto &&self, ld l, ld r, ld u, ld v, ld w,
                       ld s, ld tol, int left) -> Result
        {
            ld m = midpoint(l, r), x = midpoint(l, m), y = midpoint(m, r);
            if (m == l || m == r || x == l || x == m || y == m || y == r ||
                used > limit - 2)
                return {s, inf, 0, false};
            ld fx = f(x), fy = f(y);
            used += 2;
            ld sl = area(l, m, u, fx, v), sr = area(m, r, v, fy, w);
            ld sum = sl + sr, delta = sum - s;
            ld value = sum + delta / 15, error = abs(delta) / 15;
            if (!isfinite(fx) || !isfinite(fy) || !isfinite(sl) ||
                !isfinite(sr) || !isfinite(value) || !isfinite(error))
                return {s, inf, 0, false};
            if (error <= tol) return {value, error, 0, true};
            if (!left || tol / 2 == 0) return {value, error, 0, false};
            auto p = self(self, l, m, u, fx, v, sl, tol / 2, left - 1);
            auto q = self(self, m, r, v, fy, w, sr, tol / 2, left - 1);
            value = p.value + q.value;
            error = p.error + q.error;
            if (!isfinite(value)) return {s, inf, 0, false};
            return {value, error, 0, p.met && q.met && error <= tol};
        };
        auto answer = rec(rec, a, b, fa, fm, fb, whole, eps, depth);
        if (reverse) answer.value = -answer.value;
        answer.evaluations = used;
        return answer;
    }
};
