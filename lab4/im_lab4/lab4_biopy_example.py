from Bio import SeqIO

record = SeqIO.read("sample2.gb", "genbank")

print("------------------------------------------------------ RECORD: ")
print(record)
print()

print("------------------------------------------------------ SEQUENCE: ")
print(record.seq)
print()

print("------------------------------------------------------ FEATURES: ")
print(record.features)
print()

print("------------------------------------------------------ GENE: ")
# fragment sekwencji z pojedynczym genem (na podstawie lokalizacji w features)
gene = record.seq[3299:4037]
print(gene)
print()

print("------------------------------------------------------ PROTEIN: ")
# t³umaczenie genu na bia³ko
prot = gene.translate()
print(prot)
print()
