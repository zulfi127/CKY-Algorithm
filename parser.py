# Implementation of CKY algorithm
"""
CKY algorithm from the "Natural Language Processing" course by Michael Collins
https://class.coursera.org/nlangp-001/class
"""
import sys
from sys import stdin, stderr
from time import time
from json import dumps

from collections import defaultdict
from pprint import pprint

from pcfg import PCFG
from tokenizer import PennTreebankTokenizer

def argmax(lst):
    return max(lst) if lst else (0.0, None)

def backtrace(back, bp):
    # Extract the tree from the backpointers
    # preterminals : (C, w, min, max)
    # Binary: (C, C1, C2, min, mid, max)
    if len(back) == 4:
        return [back[0], back[1]]
    if len(back) == 6:
        return [back[0], backtrace(bp[back[3], back[4], back[1]], bp), backtrace(bp[back[4], back[5], back[2]], bp)]
    
def CKY(pcfg, norm_words):
    # IMPLEMENT CKY
    # Initialize your charts (for scores and backpointers)
    n = len(norm_words)
    pi = defaultdict(float)
    bp = defaultdict(tuple)

    # Code for adding the words to the chart
    for i in range(n):
        for sym in pcfg.N:
            pi[i, i+1, sym] = pcfg.q1[sym, norm_words[i][0]]
            bp[i, i+1, sym] = (sym, norm_words[i][1], i, i+1)

            
    # Code for the dynamic programming part, where larger and larger subtrees are built
    for j in range(2, n+1):
        for i in range(j-2, -1, -1):
            for sym in pcfg.N:
                max_score = 0.0
                back = ()
                for rule in pcfg.binary_rules[sym]:
                    for s in range(i+1, j):
                        t1 = pi[i, s, rule[0]]
                        t2 = pi[s, j, rule[1]]
                        score = t1 * t2 * pcfg.q2[sym, rule[0], rule[1]]
                        if score > max_score:
                            max_score = score
                            back = (sym, rule[0], rule[1], i, s, j)                         
                pi[i, j, sym] =  max_score
                bp[i, j, sym] = back

    return backtrace(bp[0, n, "S"], bp) # one option for retrieving the best trees
                


class Parser:
    def __init__(self, pcfg):
        self.pcfg = pcfg
        self.tokenizer = PennTreebankTokenizer()
    
    def parse(self, sentence):
        words = self.tokenizer.tokenize(sentence)
        norm_words = []
        for word in words:                # rare words normalization + keep word
            norm_words.append((self.pcfg.norm_word(word), word))
        tree = CKY(self.pcfg, norm_words)
        tree[0] = tree[0].split("|")[0]
        return tree
    
def display_tree(tree):
    pprint(tree)

if __name__ == "__main__":

    if len(sys.argv) != 2:
        print("usage: python3 parser.py GRAMMAR")
        exit()

    start = time()
    grammar_file = sys.argv[1]
    print("Loading grammar from " + grammar_file + " ...", file=stderr)    
    pcfg = PCFG()
    pcfg.load_model(grammar_file)
    parser = Parser(pcfg)

    for sentence in stdin:
        tree = parser.parse(sentence)
        print(dumps(tree))
    print("Time: (%.2f)s\n" % (time() - start), file=stderr)
