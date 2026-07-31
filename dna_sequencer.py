import random
from collections import Counter

CODON_TABLE = {
    'TTT':'F','TTC':'F','TTA':'L','TTG':'L','CTT':'L','CTC':'L',
    'CTA':'L','CTG':'L','ATT':'I','ATC':'I','ATA':'I','ATG':'M',
    'GTT':'V','GTC':'V','GTA':'V','GTG':'V','TCT':'S','TCC':'S',
    'TCA':'S','TCG':'S','CCT':'P','CCC':'P','CCA':'P','CCG':'P',
    'ACT':'T','ACC':'T','ACA':'T','ACG':'T','GCT':'A','GCC':'A',
    'GCA':'A','GCG':'A','TAT':'Y','TAC':'Y','TAA':'*','TAG':'*',
    'CAT':'H','CAC':'H','CAA':'Q','CAG':'Q','AAT':'N','AAC':'N',
    'AAA':'K','AAG':'K','GAT':'D','GAC':'D','GAA':'E','GAG':'E',
    'TGT':'C','TGC':'C','TGA':'*','TGG':'W','CGT':'R','CGC':'R',
    'CGA':'R','CGG':'R','AGT':'S','AGC':'S','AGA':'R','AGG':'R',
    'GGT':'G','GGC':'G','GGA':'G','GGG':'G',
}

AMINO_NAMES = {
    'F':'Phe','L':'Leu','I':'Ile','M':'Met','V':'Val','S':'Ser',
    'P':'Pro','T':'Thr','A':'Ala','Y':'Tyr','H':'His','Q':'Gln',
    'N':'Asn','K':'Lys','D':'Asp','E':'Glu','C':'Cys','W':'Trp',
    'R':'Arg','G':'Gly','*':'STOP',
}

def random_dna(length):
    return ''.join(random.choice('ATCG') for _ in range(length))

def complement(dna):
    pairs = {'A':'T', 'T':'A', 'C':'G', 'G':'C'}
    return ''.join(pairs[b] for b in dna)

def transcribe(dna):
    return dna.replace('T', 'U')

def translate(dna):
    protein = []
    for i in range(0, len(dna) - 2, 3):
        codon = dna[i:i+3]
        amino = CODON_TABLE.get(codon, '?')
        if amino == '*':
            break
        protein.append(amino)
    return ''.join(protein)

def find_orfs(dna, min_length=30):
    orfs = []
    for frame in range(3):
        i = frame
        start = None
        while i < len(dna) - 2:
            codon = dna[i:i+3]
            if codon == 'ATG' and start is None:
                start = i
            elif CODON_TABLE.get(codon) == '*' and start is not None:
                if i - start >= min_length:
                    orfs.append((start, i + 3, dna[start:i+3]))
                start = None
            i += 3
    return orfs

def gc_content(dna):
    gc = sum(1 for b in dna if b in 'GC')
    return gc / len(dna) * 100

def find_motif(dna, pattern):
    positions = []
    for i in range(len(dna) - len(pattern) + 1):
        if dna[i:i+len(pattern)] == pattern:
            positions.append(i)
    return positions

def mutation_rate(dna1, dna2):
    if len(dna1) != len(dna2):
        return -1
    diffs = sum(1 for a, b in zip(dna1, dna2) if a != b)
    return diffs / len(dna1) * 100

def visualize_dna(dna, width=60):
    colors = {'A':'\033[91m', 'T':'\033[93m', 'C':'\033[94m', 'G':'\033[92m'}
    reset = '\033[0m'
    lines = []
    for i in range(0, len(dna), width):
        chunk = dna[i:i+width]
        colored = ''.join(f"{colors[b]}{b}{reset}" for b in chunk)
        comp = complement(chunk)
        comp_colored = ''.join(f"{colors[b]}{b}{reset}" for b in comp)
        bonds = ''.join('|' for _ in chunk)
        lines.append(f"  5' {colored} 3'")
        lines.append(f"     {bonds}")
        lines.append(f"  3' {comp_colored} 5'")
        lines.append("")
    return '\n'.join(lines)

def codon_frequency(dna):
    codons = [dna[i:i+3] for i in range(0, len(dna)-2, 3)]
    return Counter(codons)


if __name__ == "__main__":
    random.seed(42)
    dna = random_dna(300)

    start_idx = random.randint(20, 50)
    dna = dna[:start_idx] + 'ATG' + random_dna(90) + 'TAA' + dna[start_idx:]

    print("=" * 65)
    print("  🧬 DNA Sequencer & Analyzer")
    print("=" * 65)

    print(f"\n  Sequence length: {len(dna)} bp")
    print(f"  GC content: {gc_content(dna):.1f}%")

    print(f"\n  Base composition:")
    for base in 'ATCG':
        count = dna.count(base)
        bar = '█' * (count // 5)
        print(f"    {base}: {count:>3} ({count/len(dna)*100:.1f}%) {bar}")

    print(f"\n  Double helix visualization:")
    print(visualize_dna(dna[:120]))

    rna = transcribe(dna)
    print(f"  mRNA (first 60): {rna[:60]}...")

    orfs = find_orfs(dna)
    print(f"\n  Open Reading Frames found: {len(orfs)}")
    for start, end, seq in orfs[:3]:
        protein = translate(seq)
        print(f"    ORF at {start}-{end} ({end-start} bp)")
        print(f"    Protein: {protein[:30]}{'...' if len(protein) > 30 else ''}")
        print(f"    Amino acids: {', '.join(AMINO_NAMES.get(a, '?') for a in protein[:8])}")

    motif = "ATG"
    positions = find_motif(dna, motif)
    print(f"\n  Motif '{motif}' found at {len(positions)} positions: {positions[:10]}")

    mutant = list(dna)
    for _ in range(15):
        pos = random.randint(0, len(mutant) - 1)
        mutant[pos] = random.choice('ATCG')
    mutant = ''.join(mutant)
    print(f"\n  Mutation rate vs mutant: {mutation_rate(dna, mutant):.2f}%")

    freq = codon_frequency(dna[:90])
    print(f"\n  Top 10 codons (first 90bp):")
    for codon, count in freq.most_common(10):
        amino = CODON_TABLE.get(codon, '?')
        print(f"    {codon} ({AMINO_NAMES.get(amino, '?'):>4}) : {'█' * count} {count}")
