#include "../src/compact/batch_units.hpp"
#include "../src/compact/dynamic_modint.hpp"

int main()
{
    using Z = mint<>;
    for (int p = 1; p <= 100; p++)
    {
        Z::set_mod(p);
        assert(batch_units(vector<Z>{})->empty());
        for (int a = 0; a < p; a++)
            for (int b = 0; b < p; b++)
            {
                auto inv = batch_units(vector<Z>{Z(a), Z(b)});
                bool valid = gcd(a, p) == 1 && gcd(b, p) == 1;
                assert(inv.has_value() == valid);
                if (valid)
                {
                    assert(a * (*inv)[0].v % p == 1 % p);
                    assert(b * (*inv)[1].v % p == 1 % p);
                }
            }
    }
    Z::set_mod(998244353);
    mt19937 rng(65421);
    vector<Z> a(10000);
    for (auto &x : a) x = rng() % (Z::mod - 1) + 1;
    auto original = a;
    auto inv = batch_units(a);
    assert(a == original);
    for (int i = 0; i < int(a.size()); i++)
        assert(1LL * a[i].v * (*inv)[i].v % Z::mod == 1);
    a[1234] = 0;
    assert(!batch_units(move(a)));
    cout << "Generic batch units: exhaustive composite units/nonunits, empty input and "
            "independent product certificates PASS\n";
}
