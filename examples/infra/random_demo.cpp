#include "random_tools.hpp"

int main(int argc, char** argv) {
    if (argc > 1) {
        rng.seed(stoull(argv[1]));
    }
    bernoulli_distribution coin(0.3);
    normal_distribution<double> normal(0.0, 1.0);
    discrete_distribution<int> weighted{1, 2, 7};
    cout << coin(rng) << ' ' << normal(rng) << ' ' << weighted(rng) << '\n';
    auto p = permutation(10);
    vector<int> chosen;
    sample(p.begin(), p.end(), back_inserter(chosen), 3, rng);
    for (int x : chosen) {
        cout << x << ' ';
    }
    cout << '\n';
    cout << random_int(-10, 10) << ' ' << random_real(0, 1) << '\n';
    cout << random_string(12, "abc") << '\n';
    auto edges = random_graph(6, 8);
    cout << 6 << ' ' << edges.size() << '\n';
    for (auto [u, v] : edges) {
        cout << u << ' ' << v << '\n';
    }
}
