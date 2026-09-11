#include "../src/compact/lex_two_sat.hpp"
#include "../src/classic/lex_two_sat.hpp"
#include <array>
#include <optional>
#include <random>
#include <iostream>
#include <pthread.h>

optional<vector<int>> brute(int n, const vector<array<int, 4>> &clauses)
{
    for (int mask = 0; mask < (1 << n); mask++)
    {
        vector<int> value(n + 1);
        for (int x = 1; x <= n; x++)
            value[x] = mask >> (n - x) & 1;
        bool valid = true;
        for (auto [x, a, y, b] : clauses)
            if (value[x] != a && value[y] != b)
                valid = false;
        if (valid)
            return value;
    }
    return nullopt;
}

void check(int n, const vector<array<int, 4>> &clauses)
{
    LexTwoSAT a(n);
    static Lex_Two_SAT<9> b;
    b.Init(n);
    vector<array<int, 4>> prefix;
    auto verify = [&]()
    {
        auto expected = brute(n, prefix);
        for (int repeat = 0; repeat < 2; repeat++)
        {
            assert(a.solve() == expected.has_value());
            assert(b.Solve() == expected.has_value());
            if (expected)
                assert(a.answer == *expected && b.answer == *expected);
            else
                assert(a.answer.empty() && b.answer.empty());
        }
    };
    verify();
    for (auto [x, v, y, w] : clauses)
    {
        a.add(x, v, y, w);
        b.Add(x, v, y, w);
        assert(a.answer.empty() && b.answer.empty());
        prefix.push_back({x, v, y, w});
        verify();
    }
    for (int x = 1; x <= n; x++)
    {
        a.force(x, x % 2);
        b.Force(x, x % 2);
        prefix.push_back({x, x % 2, x, x % 2});
        verify();
    }
    b.Init(n);
    assert(b.Solve() && b.answer == vector<int>(n + 1));
}

void *large(void *)
{
    constexpr int n = 100000;
    LexTwoSAT a(n);
    static Lex_Two_SAT<n> b;
    b.Init(n);
    for (int x = 1; x < n; x++)
    {
        a.add(x, true, x + 1, false);
        a.add(x, false, x + 1, true);
        b.Add(x, true, x + 1, false);
        b.Add(x, false, x + 1, true);
    }
    a.force(n, true);
    b.Force(n, true);
    assert(a.solve() && b.Solve());
    for (int x = 1; x <= n; x++)
        assert(a.answer[x] == 1 && b.answer[x] == 1);
    a.force(1, false);
    b.Force(1, false);
    assert(!a.solve() && !b.Solve());
    assert(a.answer.empty() && b.answer.empty());
    return nullptr;
}

int main()
{
    check(0, {});
    for (int n = 1; n <= 2; n++)
    {
        vector<array<int, 4>> possible;
        for (int u = 0; u < 2 * n; u++)
            for (int v = u; v < 2 * n; v++)
                possible.push_back({u / 2 + 1, u % 2, v / 2 + 1, v % 2});
        for (int mask = 0; mask < (1 << possible.size()); mask++)
        {
            vector<array<int, 4>> clauses;
            for (int i = 0; i < (int)possible.size(); i++)
                if (mask >> i & 1)
                    clauses.push_back(possible[i]);
            check(n, clauses);
        }
    }
    mt19937 rng(1814);
    for (int test = 0; test < 350; test++)
    {
        int n = rng() % 9 + 1;
        vector<array<int, 4>> clauses;
        int m = rng() % 35;
        for (int i = 0; i < m; i++)
            clauses.push_back({(int)(rng() % n) + 1, (int)(rng() % 2),
                               (int)(rng() % n) + 1, (int)(rng() % 2)});
        check(n, clauses);
    }
    pthread_attr_t attr;
    assert(pthread_attr_init(&attr) == 0);
    assert(pthread_attr_setstacksize(&attr, 512ULL << 20) == 0);
    pthread_t worker;
    assert(pthread_create(&worker, &attr, large, nullptr) == 0);
    assert(pthread_join(worker, nullptr) == 0);
    pthread_attr_destroy(&attr);
    cout << "Lex 2-SAT dual exhaustive assignment oracle, incremental/forced clauses, rollback and 100000-variable recursive chain PASS\n";
}
