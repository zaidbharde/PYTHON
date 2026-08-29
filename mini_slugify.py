import re

text = "A Tiny Python Block!"
print(re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-"))
