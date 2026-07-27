import random
from collections import defaultdict

text = "the quick brown fox jumps over the lazy dog and the fox runs fast"
words = text.split()
model = defaultdict(list)
for i in range(len(words)-1):
    model[words[i]].append(words[i+1])

def generate(n=15):
    word = random.choice(words)
    result = [word]
    for _ in range(n):
        if word not in model: break
        word = random.choice(model[word])
        result.append(word)
    return ' '.join(result)

print(generate())
