from collections import deque

class AhoCorasick:
    def __init__(self):
        self.trie = {0: {}}
        self.fail = {0: 0}
        self.output = {0: []}
        self.count = 1

    def add_pattern(self, pattern):
        node = 0
        for ch in pattern:
            if ch not in self.trie[node]:
                self.trie[self.count] = {}
                self.fail[self.count] = 0
                self.output[self.count] = []
                self.trie[node][ch] = self.count
                self.count += 1
            node = self.trie[node][ch]
        self.output[node].append(pattern)

    def build(self):
        queue = deque()
        for ch, child in self.trie[0].items():
            self.fail[child] = 0
            queue.append(child)

        while queue:
            node = queue.popleft()
            for ch, child in self.trie[node].items():
                queue.append(child)
                f = self.fail[node]
                while f and ch not in self.trie[f]:
                    f = self.fail[f]
                self.fail[child] = self.trie[f].get(ch, 0) if ch in self.trie[f] else 0
                self.output[child] += self.output[self.fail[child]]

    def search(self, text):
        node = 0
        results = []
        for i, ch in enumerate(text):
            while node and ch not in self.trie[node]:
                node = self.fail[node]
            node = self.trie[node].get(ch, 0)
            for pattern in self.output[node]:
                results.append((i - len(pattern) + 1, pattern))
        return results


if __name__ == "__main__":
    ac = AhoCorasick()
    for word in ["he", "she", "his", "hers"]:
        ac.add_pattern(word)
    ac.build()
    print(ac.search("ahishers"))
