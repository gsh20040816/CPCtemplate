#include "../src/compact/segment_li_chao.hpp"
#include <boost/multiprecision/cpp_int.hpp>
#include <iostream>
#include <random>
using namespace std;
using boost::multiprecision::cpp_int;

int main()
{
    mt19937_64 rng(4097);
    auto check = [&](const SegmentLiChao &t)
    {
        for (auto x : t.xs)
        {
            int want = 0;
            cpp_int best_num = 0, best_den = 1;
            for (int id = 1; id < (int)t.lines.size(); id++)
            {
                auto [a, b, c, d] = t.lines[id];
                if (x < a || x > c) continue;
                cpp_int den = c == a ? 1 : c - a;
                cpp_int num = c == a ? cpp_int(max(b, d))
                                     : cpp_int(b) * (c - x) + cpp_int(d) * (x - a);
                if (!want || num * best_den > best_num * den)
                {
                    want = id;
                    best_num = num;
                    best_den = den;
                }
            }
            assert(t.query(x) == want);
        }
    };
    for (int trial = 0; trial < 150; trial++)
    {
        vector<long long> xs;
        for (int x = -12; x <= 12; x++) xs.push_back(x);
        xs.push_back(0);
        shuffle(xs.begin(), xs.end(), rng);
        SegmentLiChao t(xs);
        check(t);
        for (int i = 0; i < 80; i++)
        {
            auto a = (long long)(rng() % 35) - 17;
            auto b = (long long)(rng() % 31) - 15;
            auto c = (long long)(rng() % 35) - 17;
            auto d = (long long)(rng() % 31) - 15;
            assert(t.add(a, b, c, d) == i + 1);
            check(t);
        }
    }
    SegmentLiChao extreme({-1000000000, -999999999, -1, 0, 1, 999999999, 1000000000});
    for (long long y : {-2000000000000000000LL, 0LL, 2000000000000000000LL})
    {
        extreme.add(-1000000000, y, 1000000000, -y);
        extreme.add(1000000000, y, -1000000000, -y);
        extreme.add(0, y, 0, -y);
        check(extreme);
    }
    SegmentLiChao close({1});
    close.add(0, 0, 999999999, 1);
    close.add(0, 0, 999999998, 1);
    assert(close.query(1) == 2);
    close.add(0, 0, 999999998, 1);
    assert(close.query(1) == 2);
    check(close);
    cout << "SegmentLiChao: cpp_int rational scan, 150x80 insertions, "
            "empty/vertical/reversed/tied segments, signed coordinate bounds and "
            "sub-epsilon separation PASS\n";
}
