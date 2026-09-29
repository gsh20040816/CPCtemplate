#pragma once
#include "fft.hpp"

// BEGIN convolution_fft
// IEEE nearest rounding, root error <= 8 * 2^-53; no fast-math.
vector<long long> convolution_fft(const vector<int> &a, const vector<int> &b)
{
    if (a.empty() || b.empty()) return {};
    assert(a.size() + b.size() - 1 <= ComplexFFT::max_size);
    long double ma = 0, mb = 0;
    for (int v : a) ma = max(ma, fabsl((long double)v));
    for (int v : b) mb = max(mb, fabsl((long double)v));
    assert(ma * mb * sqrtl((long double)a.size() * b.size()) <= 2e12L);
    int size = a.size() + b.size() - 1, n = 1;
    while (n < size) n *= 2;
    ComplexFFT fft(n);
    vector<ComplexFFT::C> x(n), y(n);
    for (int i = 0; i < (int)a.size(); i++) x[i] = a[i];
    for (int i = 0; i < (int)b.size(); i++) y[i] = b[i];
    fft.transform(x);
    fft.transform(y);
    for (int i = 0; i < n; i++) x[i] *= y[i];
    fft.transform(x, true);
    vector<long long> result(size);
    for (int i = 0; i < size; i++) result[i] = llroundl(x[i].real());
    return result;
}

// END convolution_fft
