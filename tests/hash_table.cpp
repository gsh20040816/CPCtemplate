#include "../src/compact/hash_table.hpp"

int main()
{
    gp_map<uint64_t, uint64_t> a;
    map<uint64_t, uint64_t> b;
    mt19937_64 rng(43861);
    vector<uint64_t> keys{0, 1, UINT64_MAX, 1ULL << 63};
    for (int i = 0; i < 3000; i++) keys.push_back(rng());
    for (int t = 0; t < 100000; t++)
    {
        uint64_t k = keys[rng() % keys.size()], v = rng();
        switch (rng() % 4)
        {
        case 0:
            a[k] = v;
            b[k] = v;
            break;
        case 1:
            assert(a.erase(k) == b.erase(k));
            break;
        case 2:
        {
            auto x = a.insert({k, v});
            auto y = b.insert({k, v});
            assert(x.second == y.second);
            assert(x.first->second == y.first->second);
            break;
        }
        default:
        {
            auto x = a.find(k);
            auto y = b.find(k);
            assert((x == a.end()) == (y == b.end()));
            if (x != a.end()) assert(x->second == y->second);
        }
        }
        assert(a.size() == b.size());
    }
    auto c = a;
    a.clear();
    assert(a.empty());
    for (auto [k, v] : b) assert(c.find(k)->second == v);
    gp_map<int64_t, int> signed_keys;
    signed_keys[INT64_MIN] = 1;
    signed_keys[INT64_MAX] = 2;
    signed_keys[-1] = 3;
    assert(signed_keys.size() == 3 && signed_keys[INT64_MIN] == 1);
    for (uint64_t i = 0; i < 1000000; i++) a[i << 20] = i ^ 42;
    for (uint64_t i = 0; i < 1000000; i++) assert(a.find(i << 20)->second == (i ^ 42));
    cout << "gp_map ordered-map oracle, erase/insert/copy/clear, signed64 "
            "extremes and million sparse keys PASS\n";
}
