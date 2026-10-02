#include <bits/stdc++.h>
#include <cassert>
#include "../src/compact/pbds_heap.hpp"
using namespace std;

struct Trace
{
    static inline int copies = 0, moves = 0;
    Trace() = default;
    Trace(const Trace &) { copies++; }
    Trace(Trace &&) noexcept { moves++; }
};

void test_move()
{
    Trace a;
    auto &&r = std::move(a);
    assert(&r == &a && Trace::copies == 0 && Trace::moves == 0);
    Trace b(std::move(a));
    const Trace c;
    Trace d(std::move(c));
    assert(Trace::copies == 1 && Trace::moves == 1);
    vector<int> x{1, 2, 3};
    vector<int> y = std::move(x);
    assert((y == vector<int>{1, 2, 3}));
    x.clear();
    x.push_back(7);
    assert(x[0] == 7);
    const vector<int> z{4, 5};
    vector<int> w = std::move(z);
    w[0] = 9;
    assert(z[0] == 4);
}

void test_ranges()
{
    vector<int> v{3, 2, 3, 7, 1};
    sort(v.begin(), v.end());
    v.erase(unique(v.begin(), v.end()), v.end());
    assert((v == vector<int>{1, 2, 3, 7}));
    assert(*lower_bound(v.begin(), v.end(), 7) == 7);
    assert(lower_bound(v.begin(), v.end(), 8) == v.end());
    priority_queue<int, vector<int>, greater<int>> q;
    q.push(7);
    q.push(2);
    assert(q.top() == 2);
    q.pop();
    assert(q.top() == 7);
    multiset<int> s{3, 3, 4};
    s.erase(s.find(3));
    assert(s.count(3) == 1);
    optional<int> zero = 0;
    assert(zero && *zero == 0);

    // Show the broken equivalence relation without invoking sort on invalid input.
    if (numeric_limits<double>::has_quiet_NaN)
    {
        double nan = numeric_limits<double>::quiet_NaN();
        auto equiv = [](double a, double b) { return !(a < b) && !(b < a); };
        assert(equiv(1, nan) && equiv(nan, 2) && !equiv(1, 2));
    }
}

void test_numeric()
{
    vector<int> a{1000000000, 1000000000, 1000000000};
    assert(accumulate(a.begin(), a.end(), 0LL) == 3000000000LL);
    vector<int> empty;
    assert(accumulate(empty.begin(), empty.end(), 9LL) == 9);
    int x = 1000000000, y = 3;
    static_assert(is_same_v<decltype(x * y), int>);
    static_assert(is_same_v<decltype(1LL * x * y), long long>);
    assert(1LL * x * y == 3000000000LL);

    vector<long long> prefix(a.begin(), a.end());
    auto end = partial_sum(prefix.begin(), prefix.end(), prefix.begin());
    assert(end == prefix.end());
    assert((prefix == vector<long long>{1000000000, 2000000000, 3000000000}));

    // A wide output does not widen the accumulator. Keep the int sums in range.
    vector<int> small{2, 3, 4};
    vector<long long> out(small.size());
    int calls = 0;
    partial_sum(small.begin(), small.end(), out.begin(), [&](auto sum, auto value)
    {
        static_assert(is_same_v<decltype(sum), int>);
        static_assert(is_same_v<decltype(value), int>);
        calls++;
        return sum + value;
    });
    assert(calls == 2 && (out == vector<long long>{2, 5, 9}));
    out.assign(1, 17);
    assert(partial_sum(empty.begin(), empty.end(), out.begin()) == out.begin());
    assert(out[0] == 17);
    vector<int> singleton{6};
    partial_sum(singleton.begin(), singleton.end(), singleton.begin());
    assert(singleton[0] == 6);
}

void test_tuple()
{
    long long a = 17, b = 5;
    auto refs = tie(a, b);
    auto saved = pair{a, b};
    static_assert(is_same_v<decltype(refs), tuple<long long &, long long &>>);
    long long q = a / b;
    tie(a, b) = pair{b, a - q * b};
    assert(a == 5 && b == 2);
    assert(get<0>(refs) == 5 && get<1>(refs) == 2);
    assert(saved.first == 17 && saved.second == 5);
    tie(a, b) = pair{b, a};
    assert(a == 2 && b == 5);

    vector<int> weight{5, 1, 5, 1}, ids(weight.size());
    iota(ids.begin(), ids.end(), 0);
    sort(ids.begin(), ids.end(), [&](int x, int y)
    {
        return tie(weight[x], x) < tie(weight[y], y);
    });
    assert((ids == vector<int>{1, 3, 0, 2}));
}

void test_complex()
{
    using C = complex<long double>;
    C z(3, 4);
    assert(z.real() == 3 && z.imag() == 4);
    assert(conj(z) == C(3, -4));
    assert(abs(z) == 5 && norm(z) == 25);
    assert(z * conj(z) == C(25, 0));
    // Multiplying by i and then its conjugate recovers the original value.
    C root(0, 1);
    assert(z * root == C(-4, 3));
    assert((z * root) * conj(root) == z);
    assert(abs(C()) == 0 && norm(C()) == 0);
}

void test_bits()
{
    static_assert(bit_width(0u) == 0);
    static_assert(bit_width(8u) == 4);
    static_assert(popcount(10u) == 2);
    static_assert(countr_zero(0u) == numeric_limits<unsigned>::digits);
    static_assert(countl_zero(0u) == numeric_limits<unsigned>::digits);
    static_assert(popcount(0u) == 0);
    // Independent division/remainder oracle; never call GCC clz/ctz on zero.
    for (unsigned x = 0; x < 65536; x++)
    {
        int width = 0, ones = 0, trailing = numeric_limits<unsigned>::digits;
        for (unsigned v = x; v; v /= 2)
        {
            width++;
            ones += v % 2;
        }
        if (x)
        {
            trailing = 0;
            for (unsigned v = x; v % 2 == 0; v /= 2) trailing++;
            assert(__builtin_ctz(x) == trailing);
            assert(__builtin_clz(x) == numeric_limits<unsigned>::digits - width);
        }
        assert(bit_width(x) == width);
        assert(popcount(x) == ones);
        assert(countr_zero(x) == trailing);
        assert(countl_zero(x) == numeric_limits<unsigned>::digits - width);
    }
    using U = unsigned long long;
    constexpr int digits = numeric_limits<U>::digits;
    U high = 1ULL << (digits - 1), all = numeric_limits<U>::max();
    assert(bit_width(high) == digits && popcount(high) == 1);
    assert(countr_zero(high) == digits - 1 && countl_zero(high) == 0);
    assert(__builtin_ctzll(high) == digits - 1 && __builtin_clzll(high) == 0);
    assert(bit_width(all) == digits && popcount(all) == digits);
    assert(countr_zero(all) == 0 && countl_zero(all) == 0);
    U reference = 0;
    for (int k = 0; k < 64; k++)
    {
        U mask = (1ULL << k) - 1;
        assert(mask == reference && popcount(mask) == k);
        reference = reference * 2 + 1;
    }
    // Layer counts around zero, singleton and powers of two, as used by wavelets.
    for (int n : {0, 1, 2, 3, 4, 5, 8, 9})
    {
        int expected = 0;
        for (int capacity = 1; capacity < n; capacity *= 2) expected++;
        assert(bit_width((unsigned)max(1, n) - 1) == expected);
    }
}

void test_random()
{
    // Only compare within this implementation, never to a fixed shuffle output.
    for (int n : {0, 1, 2, 7, 64, 127})
    {
        vector<int> a(n);
        for (int i = 0; i < n; i++) a[i] = i % 5;
        auto b = a, sorted = a;
        mt19937_64 rng(20260913), replay(20260913);
        shuffle(a.begin(), a.end(), rng);
        shuffle(b.begin(), b.end(), replay);
        assert(a == b && rng == replay);
        sort(a.begin(), a.end());
        sort(sorted.begin(), sorted.end());
        assert(a == sorted);
    }
    mt19937_64 rng(20260913), replay(20260913);
    uniform_int_distribution<int> dist(-3, 7), same(-3, 7), fixed(4, 4);
    assert(dist.min() == -3 && dist.max() == 7);
    for (int i = 0; i < 1000; i++)
    {
        int x = dist(rng);
        assert(-3 <= x && x <= 7 && x == same(replay));
    }
    assert(fixed(rng) == 4);
}

void test_pbds()
{
    pheap<int> first, second;
    auto h = first.push(7);
    first.modify(h, 2);
    second.join(first);
    assert(first.empty() && second.top() == 2);
    second.erase(h);
    assert(second.empty());
}

int main()
{
    test_move();
    test_ranges();
    test_numeric();
    test_tuple();
    test_complex();
    test_bits();
    test_random();
    test_pbds();
    cout << "Infra C++ examples: move, ranges/NaN, numeric prefixes, tuple references, "
         << "complex, bit boundaries (65536 values), shuffle and PBDS PASS\n";
}
