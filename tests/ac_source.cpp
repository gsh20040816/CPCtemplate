#include "../src/compact/ac_shortest.hpp"
namespace original
{
constexpr int max1 = 4096, inf = INT_MAX;
#include "../build/automata-source/ac_automaton.cpp"
Aho_Corsick_Automaton ac;
}

long long checks = 0;
void check(const vector<string> &patterns, const vector<string> &texts)
{
    auto &source = original::ac;
    source.Clear();
    AhoCorasick current;
    vector<pair<int, int>> ends;
    for (auto &p : patterns)
    {
        source.Insert(p);
        ends.push_back({current.add(p), p.size()});
    }
    source.Build();
    current.build();
    auto minimum = ac_shortest(current, ends);
    for (auto &text : texts)
    {
        int p = 0, q = 0;
        for (int i = 0; i < (int)text.size(); i++)
        {
            p = source.tree[p][text[i] - 'a'];
            q = current.a[q].go[text[i] - 'a'];
            int expected = INT_MAX;
            for (auto &word : patterns)
            {
                int n = word.size();
                if (n <= i + 1 && text.compare(i + 1 - n, n, word) == 0)
                    expected = min(expected, n);
            }
            assert(source.min_len[p] == expected);
            assert(minimum[q] == expected);
            checks++;
        }
    }
}

int main()
{
    vector<string> patterns, texts(1);
    for (int n = 1; n <= 6; n++)
        for (int mask = 0; mask < (1 << n); mask++)
        {
            string s(n, 'a');
            for (int i = 0; i < n; i++)
                s[i] += (mask >> i) & 1;
            texts.push_back(s);
            if (n <= 3)
                patterns.push_back(s);
        }
    int cases = 0;
    for (auto &a : patterns)
        for (auto &b : patterns)
            for (auto &c : patterns)
            {
                check({a, b, c}, texts);
                cases++;
            }
    check({}, texts);
    check({"he", "she", "e", "hers", "he"}, {"ushershe", "xyz", "sheshe"});
    mt19937 rng(1113);
    for (int trial = 0; trial < 500; trial++)
    {
        vector<string> words(rng() % 15), haystacks(10);
        for (auto &s : words)
        {
            s.resize(1 + rng() % 15);
            for (char &c : s)
                c = 'a' + rng() % 26;
        }
        for (auto &s : haystacks)
        {
            s.resize(rng() % 100);
            for (char &c : s)
                c = 'a' + rng() % 26;
        }
        check(words, haystacks);
        cases++;
    }
    cout << cases + 2 << " pattern sets; " << checks
         << " independent shortest suffix checks incl. reset, duplicate, absent PASS\n";
}
