#pragma once
#include <cassert>
#include <limits>
#include <ostream>
using namespace std;

// Default: signed 64-bit reduced values, signed 128-bit intermediates.
// Arbitrary precision: Rational<cpp_int, cpp_int> with the Boost header.
template<class T = long long, class W = __int128_t>
struct Rational
{
    T num = 0, den = 1;

    void assign(W n, W d)
    {
        assert(d != 0);
        if (d < 0)
        {
            n = -n;
            d = -d;
        }
        W a = n < 0 ? -n : n, b = d;
        while (b != 0)
        {
            W r = a % b;
            a = b;
            b = r;
        }
        n /= a;
        d /= a;
        if constexpr (numeric_limits<T>::is_bounded)
        {
            assert(n >= W(numeric_limits<T>::lowest()));
            assert(n <= W(numeric_limits<T>::max()));
            assert(d <= W(numeric_limits<T>::max()));
        }
        num = T(n);
        den = T(d);
    }

    Rational(T n = 0, T d = 1)
    {
        assign(W(n), W(d));
    }

    static Rational make(W n, W d)
    {
        Rational r;
        r.assign(n, d);
        return r;
    }

    friend Rational operator+(const Rational &a, const Rational &b)
    {
        return make(W(a.num) * b.den + W(b.num) * a.den, W(a.den) * b.den);
    }

    friend Rational operator-(const Rational &a, const Rational &b)
    {
        return make(W(a.num) * b.den - W(b.num) * a.den, W(a.den) * b.den);
    }

    friend Rational operator*(const Rational &a, const Rational &b)
    {
        return make(W(a.num) * b.num, W(a.den) * b.den);
    }

    friend Rational operator/(const Rational &a, const Rational &b)
    {
        assert(b.num != 0);
        return make(W(a.num) * b.den, W(a.den) * b.num);
    }

    Rational operator-() const
    {
        return make(-W(num), W(den));
    }

    Rational &operator+=(const Rational &b)
    {
        return *this = *this + b;
    }

    Rational &operator-=(const Rational &b)
    {
        return *this = *this - b;
    }

    Rational &operator*=(const Rational &b)
    {
        return *this = *this * b;
    }

    Rational &operator/=(const Rational &b)
    {
        return *this = *this / b;
    }

    friend bool operator==(const Rational &a, const Rational &b)
    {
        return a.num == b.num && a.den == b.den;
    }

    friend bool operator!=(const Rational &a, const Rational &b)
    {
        return !(a == b);
    }

    friend bool operator<(const Rational &a, const Rational &b)
    {
        return W(a.num) * b.den < W(b.num) * a.den;
    }

    friend bool operator>(const Rational &a, const Rational &b)
    {
        return b < a;
    }

    friend bool operator<=(const Rational &a, const Rational &b)
    {
        return !(b < a);
    }

    friend bool operator>=(const Rational &a, const Rational &b)
    {
        return !(a < b);
    }

    explicit operator double() const
    {
        return double(num) / double(den);
    }

    friend ostream &operator<<(ostream &out, const Rational &a)
    {
        out << a.num;
        if (a.den != 1)
            out << '/' << a.den;
        return out;
    }
};
