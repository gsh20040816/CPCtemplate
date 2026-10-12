#include <bits/stdc++.h>
#include <cassert>
using namespace std;
namespace source
{
#include "fixtures/wida_matrix/matrix.cpp"
}
#include "../src/compact/xor_affine64.hpp"
using U = unsigned long long;
long long checks = 0;
void check(bool ok)
{
    if (!ok)
        throw runtime_error("mismatch at " + to_string(checks));
    checks++;
}
U brute(const XorAffine64 &f, U x)
{
    U result = 0;
    for (int out = 0; out < 64; out++)
    {
        int parity = (f.bias >> out) & 1;
        for (int in = 0; in < 64; in++)
            parity ^= ((x >> in) & 1) & ((f.col[in] >> out) & 1);
        result |= U(parity) << out;
    }
    return result;
}
source::Matrix convert(const XorAffine64 &f)
{
    source::Matrix a{};
    copy(f.col.begin(), f.col.end(), a.begin());
    a[64] = f.bias;
    return a;
}
int main()
{
    mt19937_64 rng(353771);
    for (int trial = 0; trial < 180; trial++)
    {
        XorAffine64 f, g;
        f.bias = rng();
        g.bias = rng();
        for (auto &x : f.col)
            x = rng();
        for (auto &x : g.col)
            x = rng();
        auto composed = f.then(g);
        auto source_f = convert(f), source_g = convert(g);
        auto source_composed = source::operator*(source_f, source_g);
        check(convert(composed) == source_composed);
        check(convert(f.then(XorAffine64(true))) == source_f);
        check(convert(XorAffine64(true).then(f)) == source_f);
        for (U x : {0ULL, 1ULL, 1ULL << 63, ULLONG_MAX, rng()})
        {
            check(f.apply(x) == brute(f, x));
            check(source::operator*(x, source_f) == brute(f, x));
            check(composed.apply(x) == brute(g, brute(f, x)));
            int k = trial % 13;
            U value = x;
            for (int i = 0; i < k; i++)
                value = brute(f, value);
            check(f.power(k).apply(x) == value);
        }
        auto saved = f;
        auto copy = f;
        copy.col[0] ^= 1;
        copy.bias ^= 1;
        check(convert(f) == convert(saved));
    }
    // Independent per-bit rotations and bitwise expressions.
    for (int trial = 0; trial < 100; trial++)
    {
        vector<tuple<int, int, U>> operations;
        int count = trial % 17;
        stringstream input;
        input << count << '\n';
        XorAffine64 f;
        for (int j = 0; j < count; j++)
        {
            int shift = rng() % 64, op = rng() % 2;
            U mask = rng();
            operations.emplace_back(shift, op, mask);
            input << shift << ' ' << op << ' ' << mask << '\n';
            if (op == 0)
                f.bias ^= mask;
            for (int i = 0; i < 64; i++)
                f.col[i] ^= rotl(1ULL << i, shift) & (op == 0 ? ~mask : mask);
        }
        f.bias ^= rng();
        U extra = f.bias;
        for (auto [shift, op, mask] : operations)
            if (op == 0)
                extra ^= mask;
        input << extra << '\n';
        auto *previous = cin.rdbuf(input.rdbuf());
        auto matrix = source::readMatrix();
        cin.rdbuf(previous);
        check(matrix == convert(f));
        for (int j = 0; j < 20; j++)
        {
            U x = rng(), answer = extra;
            for (auto [shift, op, mask] : operations)
            {
                U rotated = 0;
                for (int i = 0; i < 64; i++)
                    rotated |= ((x >> i) & 1) << ((i + shift) % 64);
                answer ^= op == 0 ? rotated | mask : rotated & mask;
            }
            check(f.apply(x) == answer);
            check(source::operator*(x, matrix) == answer);
        }
    }
    for (U k : {0ULL, 1ULL, 2ULL, ULLONG_MAX})
    {
        XorAffine64 toggle(true), rotate;
        toggle.bias = 0xfedcba9876543210ULL;
        for (int i = 0; i < 64; i++)
            rotate.col[i] = 1ULL << ((i + 1) % 64);
        U x = rng();
        check(toggle.power(k).apply(x) == (x ^ (k & 1 ? toggle.bias : 0)));
        check(rotate.power(k).apply(x) == rotl(x, int(k % 64)));
        XorAffine64 constant;
        constant.bias = 123;
        check(constant.power(k).apply(x) == (k == 0 ? x : 123));
    }
    cout << checks << " independent affine-bit checks PASS\n";
}
