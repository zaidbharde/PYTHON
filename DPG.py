import hashlib

def dna_to_pattern(dna):
    mapping = {'A': '00', 'T': '01', 'G': '10', 'C': '11'}
    binary = ''.join([mapping[c] for c in dna if c in mapping])
    decimal = int(binary, 2)
    hashed = hashlib.sha256(str(decimal).encode()).hexdigest()
    return hashed[:16]  # Lock pattern

def verify(dna_input, stored_pattern):
    return dna_to_pattern(dna_input) == stored_pattern

# Example usage
original = "ATGCGTTA"
pattern = dna_to_pattern(original)
print("Pattern:", pattern)

# Try unlock
input_seq = input("Enter DNA: ")
if verify(input_seq, pattern):
    print("Access granted")
else:
    print("Access denied")
