#include "../src/compact/word_chain.hpp"
#include "../src/classic/word_chain.hpp"
#include <iostream>
#include <random>
#include <pthread.h>

optional<vector<string>> brute(const vector<string> &words)
{
    vector<int> ids(words.size());
    iota(ids.begin(), ids.end(), 0);
    optional<vector<string>> best;
    do
    {
        bool valid = true;
        vector<string> candidate;
        for (int i = 0; i < (int)ids.size(); i++)
        {
            if (i && words[ids[i - 1]].back() != words[ids[i]].front())
                valid = false;
            candidate.push_back(words[ids[i]]);
        }
        if (valid && (!best || candidate < *best))
            best = candidate;
    } while (next_permutation(ids.begin(), ids.end()));
    return best;
}

void check(const vector<string> &words)
{
    auto expected = brute(words);
    auto a = word_chain(words);
    auto b = Word_Chain(words);
    assert(a.has_value() == expected.has_value() && b.has_value() == expected.has_value());
    for (const auto &order : {a, b})
        if (order)
        {
            assert(order->size() == words.size());
            vector<int> used(words.size());
            vector<string> result;
            for (int id : *order)
            {
                assert(0 <= id && id < (int)words.size() && !used[id]);
                used[id] = 1;
                result.push_back(words[id]);
            }
            assert(result == *expected);
        }
}

void *large(void *)
{
    vector<string> words(200000, "aa");
    auto a = word_chain(words);
    auto b = Word_Chain(words);
    assert(a && b && a->size() == words.size() && *a == *b);
    vector<int> used(words.size());
    for (int id : *a)
    {
        assert(0 <= id && id < (int)words.size() && !used[id]);
        used[id] = 1;
    }
    return nullptr;
}

int main()
{
    vector<string> dictionary = {"a", "aa", "ab", "aba", "acb", "b", "ba", "bb"};
    // All multisets of up to five words, including equal words and prefixes.
    vector<string> words;
    auto enumerate = [&](auto &&self, int first) -> void
    {
        check(words);
        if (words.size() == 5)
            return;
        for (int i = first; i < (int)dictionary.size(); i++)
        {
            words.push_back(dictionary[i]);
            self(self, i);
            words.pop_back();
        }
    };
    enumerate(enumerate, 0);
    mt19937 rng(2337);
    for (int t = 0; t < 250; t++)
    {
        vector<string> sample;
        int n = rng() % 8;
        for (int i = 0; i < n; i++)
        {
            string word;
            int len = rng() % 5 + 1;
            for (int j = 0; j < len; j++)
                word += char('a' + rng() % 3);
            sample.push_back(word);
        }
        check(sample);
    }
    check({"aab", "aza", "ba"});
    check({"a", "b"});
    pthread_attr_t attr;
    assert(pthread_attr_init(&attr) == 0);
    assert(pthread_attr_setstacksize(&attr, 512ULL << 20) == 0);
    pthread_t worker;
    assert(pthread_create(&worker, &attr, large, nullptr) == 0);
    assert(pthread_join(worker, nullptr) == 0);
    pthread_attr_destroy(&attr);
    cout << "Word chain dual permutation oracle, word-vs-vertex order, duplicate IDs, prefixes and 200000 recursive words PASS\n";
}
