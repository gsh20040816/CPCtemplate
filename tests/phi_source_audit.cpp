// The runner prepends all four complete upstream snippets in namespaces.
void require(bool ok)
{
    if (!ok) throw runtime_error("phi source comparison failed");
}

int main()
{
    const int n = 10000000;
    LinearSieve a(n);
    source_linear::phi_and_prime_table(n);
    require(vector<int>(source_linear::prime,
                       source_linear::prime + source_linear::tot) == a.prime);
    vector<long long> sums(n + 1);
    for (int d = 1; d <= n; d++)
    {
        require(source_linear::phi[d] == a.phi[d]);
        for (int x = d; x <= n; x += d) sums[x] += a.phi[d];
    }
    for (int x = 1; x <= n; x++) require(sums[x] == x);
    source_sieve::getEuler();
    for (int x = 1; x <= 3000000; x++)
        require(source_sieve::euler[x] == a.phi[x]);
    source_sieve::euler[123] = -1;
    source_sieve::getEuler();
    require(source_sieve::euler[123] == a.phi[123]);
    for (int bound : {1, 37, 1000, 19, 100000})
    {
        source_linear::phi_and_prime_table(bound);
        LinearSieve b(bound);
        require(vector<int>(source_linear::prime,
                           source_linear::prime + source_linear::tot) == b.prime);
        for (int x = 1; x <= bound; x++)
            require(source_linear::phi[x] == b.phi[x]);
    }
    PollardRho solver;
    for (int x = 1; x <= 20000; x++)
    {
        require(source_single::eular(x) == a.phi[x]);
        require(source_factor::run(x) == a.phi[x]);
        require(euler_phi(x) == (unsigned)a.phi[x]);
        require(euler_phi(x, solver) == (unsigned)a.phi[x]);
        if (x <= 500)
        {
            int count = 0;
            for (int y = 1; y <= x; y++) count += gcd(x, y) == 1;
            require(count == a.phi[x]);
        }
    }
    // Trial primality certifies this source-loop overflow witness's phi.
    long long p = INT_MAX;
    for (long long d = 2; d <= p / d; d++) require(p % d != 0);
    require(euler_phi(p) == (unsigned long long)p - 1);
    require(euler_phi(p, solver) == (unsigned long long)p - 1);
    // First source snippet has an int accumulator despite a wider caller.
    require(source_factor::run(1LL << 32) == 0);
    require(euler_phi(1ULL << 32) == (1ULL << 31));
    require(euler_phi(1ULL << 32, solver) == (1ULL << 31));
    require(euler_phi(1ULL << 63) == (1ULL << 62));
    require(euler_phi(1ULL << 63, solver) == (1ULL << 62));
    cout << "PASS: 10M divisor identities and source linear table; 3M source sieve; "
            "20K scalar comparisons; repeated initialization and integer boundaries\n";
}
