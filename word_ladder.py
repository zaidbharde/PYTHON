from collections import deque


def ladder_length(start, target, words):
    dictionary = set(words)
    if target not in dictionary:
        return 0
    queue = deque([(start, 1)])
    while queue:
        word, distance = queue.popleft()
        if word == target:
            return distance
        for index in range(len(word)):
            for letter in "abcdefghijklmnopqrstuvwxyz":
                candidate = word[:index] + letter + word[index + 1:]
                if candidate in dictionary:
                    dictionary.remove(candidate)
                    queue.append((candidate, distance + 1))
    return 0


if __name__ == "__main__":
    words = {"hot", "dot", "dog", "lot", "log", "cog"}
    print(ladder_length("hit", "cog", words))
