def chunks(items, size):
    return [items[i:i + size] for i in range(0, len(items), size)]

print(chunks(list(range(7)), 3))
