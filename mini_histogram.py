from collections import Counter

values = [2, 2, 4, 5, 4, 2]
print(dict(sorted(Counter(values).items())))
