def rle_encode(text):
    if not text:
        return ""
    result = []
    count = 1
    for i in range(1, len(text)):
        if text[i] == text[i - 1]:
            count += 1
        else:
            result.append(f"{text[i-1]}{count}")
            count = 1
    result.append(f"{text[-1]}{count}")
    return "".join(result)


def rle_decode(encoded):
    result = []
    i = 0
    while i < len(encoded):
        char = encoded[i]
        j = i + 1
        num = ""
        while j < len(encoded) and encoded[j].isdigit():
            num += encoded[j]
            j += 1
        result.append(char * int(num))
        i = j
    return "".join(result)


if __name__ == "__main__":
    text = "aaabbbccccd"
    encoded = rle_encode(text)
    print("Encoded:", encoded)
    print("Decoded:", rle_decode(encoded))
