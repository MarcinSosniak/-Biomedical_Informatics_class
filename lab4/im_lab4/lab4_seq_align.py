from Bio.Seq import Seq
from Bio import pairwise2

seq1 = Seq("ATGGCCATTGTAATGGGCCGCTGAAAGGGTGCCCGATAG")
seq2 = Seq("GGCATTGCTAATGGCCGCTGATAGGGTGCCCGATAG")
seq3 = Seq("ATGGCATTGCTAATGGCCGCTGATAGGGTGGGCGATAG")
seq4 = Seq("GGCATTGCTTTTGGCCGCTGAGTAGGGTGCCCGGATAG")
alignments = pairwise2.align.globalms(seq1,seq2,.7,-.2,-.3,0)

def get_score(s1,s2):
    alignments = pairwise2.align.globalms(s1, s2, .7, -.2, -.3, 0)
    return alignments[0][2]


print('+---------+---------+---------+---------+---------+')
print('|         |  seq 1  |  seq 2  |  seq 3  |  seq 4  |')
print('+---------+---------+---------+---------+---------+')
print('|  seq 1  |         | {:0>2.4f} | {:0>2.4f} | {:0>2.4f} |'.format(get_score(seq1,seq2),get_score(seq1,seq3),get_score(seq1,seq4)))
print('+---------+---------+---------+---------+---------+')
print('|  seq 2  | {:0>2.4f} |         | {:0>2.4f} | {:0>2.4f} |'.format(get_score(seq2,seq1),get_score(seq2,seq3),get_score(seq2,seq4)))
print('+---------+---------+---------+---------+---------+')
print('|  seq 3  | {:0>2.4f} | {:0>2.4f} |         | {:0>2.4f} |'.format(get_score(seq3,seq1),get_score(seq3,seq2),get_score(seq3,seq4)))
print('+---------+---------+---------+---------+---------+')
print('|  seq 4  | {:0>2.4f} | {:0>2.4f} | {:0>2.4f} |         |'.format(get_score(seq4,seq1),get_score(seq4,seq2),get_score(seq4,seq3)))
print('+---------+---------+---------+---------+---------+')