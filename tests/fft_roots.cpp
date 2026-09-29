#include "../src/compact/fft.hpp"
#include <boost/math/constants/constants.hpp>
#include <boost/multiprecision/cpp_dec_float.hpp>
#include <iostream>

int main()
{
    using W = boost::multiprecision::cpp_dec_float_100;
    const int n = ComplexFFT::max_size;
    ComplexFFT fft(n);
    W angle = 2 * boost::math::constants::pi<W>() / n;
    W c = cos(angle), s = sin(angle), x = 1, y = 0;
    W unit = pow(W(2), -53), worst = 0;
    for (int i = 0; i < n / 2; i++)
    {
        W dx = W(fft.roots[i].real()) - x;
        W dy = W(fft.roots[i].imag()) - y;
        W error2 = dx * dx + dy * dy;
        if (error2 > worst) worst = error2;
        assert(error2 < 64 * unit * unit);
        W nx = x * c - y * s;
        y = x * s + y * c;
        x = nx;
    }
    std::cout << "FFT roots: all " << n / 2
              << " dyadic roots checked against 100-digit independent recurrence; "
              << "max error / 2^-53 = " << sqrt(worst) / unit
              << "; long double digits = " << std::numeric_limits<long double>::digits
              << " PASS\n";
}
