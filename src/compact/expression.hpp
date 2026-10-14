#pragma once
#include <bits/stdc++.h>
#include <cassert>
using namespace std;

// BEGIN Expression
// Integer expression: + - * / % ^, parentheses, unary + -, spaces ignored.
// Precedence: ^ (right-assoc) > unary sign > * / % > + -; / and % truncate as in C++.
struct Expression
{
    using ll = long long;
    string s;
    size_t i = 0;

    explicit Expression(string text) : s(move(text)) {}

    char peek()
    {
        while (i < s.size() && s[i] == ' ') i++;
        return i < s.size() ? s[i] : 0;
    }

    ll atom()
    {
        if (peek() == '(')
        {
            i++;
            ll v = expr();
            assert(peek() == ')');
            i++;
            return v;
        }
        assert(isdigit(peek()));
        ll v = 0;
        while (i < s.size() && isdigit(s[i])) v = v * 10 + (s[i++] - '0');
        return v;
    }

    ll power()
    {
        ll a = atom();
        if (peek() != '^') return a;
        i++;
        ll e = unary(), r = 1; // right-assoc: a^b^c = a^(b^c)
        assert(e >= 0);
        while (e)
        {
            if (e & 1) r *= a;
            if (e >>= 1) a *= a; // no square after the last bit
        }
        return r;
    }

    ll unary()
    {
        char c = peek();
        if (c == '+' || c == '-')
        {
            i++;
            ll v = unary();
            return c == '-' ? -v : v;
        }
        return power();
    }

    ll term()
    {
        ll v = unary();
        for (char c; (c = peek()) == '*' || c == '/' || c == '%';)
        {
            i++;
            ll b = unary();
            assert(c == '*' || b != 0);
            v = c == '*' ? v * b : c == '/' ? v / b : v % b;
        }
        return v;
    }

    ll expr()
    {
        ll v = term();
        for (char c; (c = peek()) == '+' || c == '-';)
        {
            i++;
            ll b = term();
            v = c == '+' ? v + b : v - b;
        }
        return v;
    }

    // Value of the whole string; the caller keeps every intermediate result within long long.
    ll eval()
    {
        i = 0;
        ll v = expr();
        assert(peek() == 0);
        return v;
    }
};
// END Expression
