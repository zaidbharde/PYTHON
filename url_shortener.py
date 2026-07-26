import hashlib
import string
import time

class URLShortener:
    BASE62 = string.ascii_letters + string.digits

    def __init__(self):
        self.url_map = {}
        self.reverse_map = {}
        self.clicks = {}

    def _hash(self, url):
        h = hashlib.md5(url.encode()).hexdigest()
        num = int(h[:10], 16)
        code = []
        while num and len(code) < 7:
            code.append(self.BASE62[num % 62])
            num //= 62
        return ''.join(code)

    def shorten(self, url):
        if url in self.reverse_map:
            return self.reverse_map[url]
        code = self._hash(url)
        while code in self.url_map:
            code = self._hash(url + str(time.time()))
        self.url_map[code] = {"url": url, "created": time.time()}
        self.reverse_map[url] = code
        self.clicks[code] = 0
        return code

    def resolve(self, code):
        if code not in self.url_map:
            return None
        self.clicks[code] += 1
        return self.url_map[code]["url"]

    def stats(self, code):
        if code not in self.url_map:
            return None
        entry = self.url_map[code]
        return {
            "code": code,
            "url": entry["url"],
            "clicks": self.clicks[code],
            "age_sec": int(time.time() - entry["created"]),
        }


if __name__ == "__main__":
    s = URLShortener()

    urls = [
        "https://www.google.com/search?q=python",
        "https://github.com/rust-lang/rust",
        "https://stackoverflow.com/questions/12345",
        "https://en.wikipedia.org/wiki/Artificial_intelligence",
        "https://www.google.com/search?q=python",
    ]

    print("=" * 55)
    print("  URL Shortener")
    print("=" * 55)

    for url in urls:
        code = s.shorten(url)
        print(f"\n  URL  : {url}")
        print(f"  Short: /{code}")

    print(f"\n{'─' * 55}")
    print("  Resolving...")

    code = s.shorten(urls[0])
    for _ in range(5):
        s.resolve(code)

    st = s.stats(code)
    print(f"\n  Code    : {st['code']}")
    print(f"  URL     : {st['url']}")
    print(f"  Clicks  : {st['clicks']}")
    print(f"  Total   : {len(s.url_map)} URLs stored")
