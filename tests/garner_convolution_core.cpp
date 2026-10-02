#include "../src/compact/garner.hpp"

// Protocol-only harness: independent arbitrary-precision oracles live in Python.
int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int cases;
    cin >> cases;
    while (cases--)
    {
        int n;
        long long target;
        cin >> n >> target;
        vector<long long> b(n), moduli(n);
        for (auto &x : b) cin >> x;
        for (auto &x : moduli) cin >> x;
        try
        {
            auto original_b = b, original_moduli = moduli;
            auto answer = garner(b, moduli, target);
            auto digits = garner_digits(b, moduli);
            assert(b == original_b && moduli == original_moduli);
            cout << answer;
            for (auto x : digits) cout << ' ' << x;
            cout << '\n';
        }
        catch (const invalid_argument &)
        {
            cout << "INVALID\n";
        }
    }
}
