#include "../src/compact/string.hpp"
#include "../src/compact/general_sam.hpp"
#include "../src/compact/online_sam.hpp"
#include "../src/compact/palindromic_tree.hpp"
namespace ordinary
{
constexpr int max1 = 2048, max2 = 26;
int Get_Id(char c)
{
    return c - 'a';
}
#include "../build/automata-source/sam.cpp"
}
namespace generalized
{
#define main original_main
#include "../build/automata-source/exSAM.cpp"
#undef main
}
namespace palindrome
{
#define main original_main
#include "../build/automata-source/PAM.cpp"
#undef main
}

struct Snapshot
{
    struct Node
    {
        array<int, 26> go;
        int link, len;
    };
    vector<Node> a;
};

template<class Original>
Snapshot snapshot(const Original &s)
{
    Snapshot result;
    for (int u = 0; u <= s.total; u++)
    {
        Snapshot::Node node;
        copy(s.trans[u], s.trans[u] + 26, node.go.begin());
        node.link = s.link[u];
        node.len = s.maxlen[u];
        result.a.push_back(node);
    }
    return result;
}

long long verifications = 0;
template<class S>
void check(const S &sam, const vector<string> &words)
{
    map<string, set<pair<int, int>>> ends;
    for (int id = 0; id < (int)words.size(); id++)
        for (int l = 0; l < (int)words[id].size(); l++)
            for (int r = l; r < (int)words[id].size(); r++)
                ends[words[id].substr(l, r - l + 1)].insert({id, r});
    map<int, set<pair<int, int>>> classes;
    set<set<pair<int, int>>> distinct;
    for (auto &[word, positions] : ends)
    {
        int u = 0;
        for (char c : word)
        {
            u = sam.a[u].go[c - 'a'];
            assert(u > 0 && u < (int)sam.a.size());
        }
        if (classes.count(u))
            assert(classes[u] == positions);
        classes[u] = positions;
        distinct.insert(positions);
        assert(sam.a[u].len >= (int)word.size());
        assert(sam.a[sam.a[u].link].len < (int)word.size());
        for (int c = 0; c < 26; c++)
            assert(bool(sam.a[u].go[c]) == ends.contains(word + char('a' + c)));
    }
    for (int c = 0; c < 26; c++)
        assert(bool(sam.a[0].go[c]) == ends.contains(string(1, char('a' + c))));
    assert(classes.size() + 1 == sam.a.size());
    assert(distinct.size() == classes.size());
    long long sum = 0;
    for (int u = 1; u < (int)sam.a.size(); u++)
    {
        assert(0 <= sam.a[u].link && sam.a[u].link < (int)sam.a.size());
        assert(sam.a[sam.a[u].link].len < sam.a[u].len);
        sum += sam.a[u].len - sam.a[sam.a[u].link].len;
    }
    assert(sum == (long long)ends.size());
    verifications++;
}

void single(const string &word)
{
    auto &source = ordinary::SAM;
    source.Clear();
    SuffixAutomaton current;
    vector<int> tags(1), prefix;
    string s;
    for (int i = 0; i < (int)word.size(); i++)
    {
        int tag = 19 * i + 7;
        source.Insert(word[i], tag);
        current.extend(word[i] - 'a');
        tags.resize(current.a.size());
        tags[current.last] = tag;
        prefix.push_back(current.last);
        s += word[i];
        check(snapshot(source), {s});
        check(current, {s});
        assert(current.a.size() == (size_t)source.total + 1);
        for (int u = 0; u <= source.total; u++)
        {
            assert(tags[u] == source.endpos[u]);
            assert(current.a[u].len == source.maxlen[u]);
            assert(current.a[u].link == source.link[u]);
            for (int c = 0; c < 26; c++)
                assert(current.a[u].go[c] == source.trans[u][c]);
        }
        auto counts = current.counts();
        vector<int> actual(current.a.size());
        for (int p : prefix)
            for (int u = p; u != -1; u = current.a[u].link)
                actual[u]++;
        for (int u = 0; u <= source.total; u++)
            assert(counts[u] == actual[u]);
    }
}

void multi(const vector<string> &words)
{
    auto &source = generalized::SAM;
    for (int u = 0; u <= source.total; u++)
        source.edge[u].clear();
    source.Clear();
    OnlineSAM online;
    GeneralSAM offline;
    vector<string> inserted;
    for (auto &s : words)
    {
        string padded = " " + s;
        source.Build(padded.c_str(), s.size());
        int p = 0;
        for (char c : s)
            p = online.extend(p, c - 'a');
        inserted.push_back(s);
        offline.add(s);
        check(snapshot(source), inserted);
        check(online, inserted);
    }
    offline.build();
    check(offline, words);
    assert(offline.a.size() == (size_t)source.total + 1);
    for (int u = 1; u <= source.total; u++)
        source.edge[source.link[u]].push_back(u);
    assert(source.Dfs(0) == offline.distinct());
    assert(online.total == offline.distinct());
}

void pam(const string &encoded)
{
    auto &source = palindrome::PAM;
    source.Clear();
    palindrome::ans = 0;
    PalindromicTree current;
    string decoded;
    int previous = 0;
    for (int i = 0; i < (int)encoded.size(); i++)
    {
        char c = 'a' + (encoded[i] - 'a' + previous) % 26;
        decoded += c;
        palindrome::s[i + 1] = c;
        source.Insert(i + 1);
        int u = current.add(c);
        int expected = 0;
        for (int l = 0; l <= i; l++)
        {
            string suffix = decoded.substr(l);
            if (equal(suffix.begin(), suffix.end(), suffix.rbegin()))
                expected++;
        }
        assert(palindrome::ans == expected);
        assert(current.t[u].suffixes == expected);
        previous = expected;
    }
}

int main()
{
    vector<string> small(1);
    for (int n = 1; n <= 3; n++)
        for (int mask = 0; mask < (1 << n); mask++)
        {
            string s(n, 'a');
            for (int i = 0; i < n; i++)
                s[i] += (mask >> i) & 1;
            small.push_back(s);
        }
    int single_cases = 0, multi_cases = 0, pam_cases = 0;
    for (int n = 0, ways = 1; n <= 7; n++, ways *= 3)
        for (int mask = 0; mask < ways; mask++)
        {
            string s(n, 'a');
            int code = mask;
            for (char &c : s)
            {
                c += code % 3;
                code /= 3;
            }
            single(s);
            pam(s);
            single_cases++;
            pam_cases++;
        }
    for (auto &a : small)
        for (auto &b : small)
            for (auto &c : small)
            {
                multi({a, b, c});
                multi_cases++;
            }
    mt19937 rng(111456);
    for (int trial = 0; trial < 500; trial++)
    {
        vector<string> words(rng() % 6);
        for (auto &s : words)
        {
            s.resize(rng() % 11);
            for (char &c : s)
                c = 'a' + rng() % 4;
        }
        multi(words);
        reverse(words.begin(), words.end());
        multi(words);
        multi_cases += 2;
        string s(50, 'a');
        for (char &c : s)
            c = 'a' + rng() % 26;
        pam(s);
        pam_cases++;
    }
    cout << single_cases << " single SAM cases; " << multi_cases
         << " generalized cases; " << pam_cases << " decoded PAM cases; "
         << verifications << " endpos oracle checks PASS\n";
}
