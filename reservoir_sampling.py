import random

def reservoir_sample(stream, k):
    reservoir = []
    for i, item in enumerate(stream):
        if i < k:
            reservoir.append(item)
        else:
            j = random.randint(0, i)
            if j < k:
                reservoir[j] = item
    return reservoir


if __name__ == "__main__":
    # simulate a large stream without loading it all into memory
    def big_stream(n):
        for i in range(n):
            yield i

    sample = reservoir_sample(big_stream(1_000_000), 5)
    print("Random 5 samples from 1M stream:", sample)
