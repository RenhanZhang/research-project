
import collections
import random
import sys

class Ngram_model:

    MAXLEN = 1000

    # text is list of paragraphs
    def __init__(self,text,n):
        self.n = n
        self.model = self.build_ngram_model(text)

    def build_ngram_model(self,text):
        ngrams = {}
        for sentence in text:
            words = sentence.split()
            previous = [None] * (self.n-1)
            words.append(None)
            for word in words:
                key = ' '.join([w for w in previous if w])
                if key not in ngrams:
                    ngrams[key] = collections.defaultdict(int)
                ngrams[key][word] += 1
                previous.pop(0)
                previous = previous + [word]
        probabilities = {}
        for ngram,words in ngrams.items():
            total = 0
            for word,count in words.items():
                total += count
            probabilities[ngram] = [ (float(count)/total,w) for w,count in words.items() ]
        return probabilities

    def get_next_word(self, ngram):
        rand = random.random()
        tot = 0
        for item in self.model[' '.join([w for w in ngram if w])]:
            tot += item[0]
            if tot > rand:
                return item[1]
        print "ERROR: got to end of list. tot =",tot,"and rand=",rand,"for ngram=",ngram

    def generate_new_text(self, num_paragraphs):
        text = ""
        for x in range(num_paragraphs):
            sentence = []
            done = False
            ngram = None
            while not done:
                if not sentence:
                    ngram = [None] * (self.n-1)
                next_word = self.get_next_word(ngram)
#print ngram,next_word
                if next_word == None:
                    text_sentence = " ".join(sentence) + '\n\n'
                    text += text_sentence
                    done = True
                else:
                    ngram.pop(0)
                    ngram = ngram + [next_word]
                    sentence.append(next_word)
                    if len(sentence) > self.MAXLEN:
                        print "WARNING: a paragraph is too long (>"+str(self.MAXLEN)+' words)'
                        text_sentence = " ".join(sentence)
                        text_sentence = text_sentence[0].upper() + text_sentence[1:] + '\n\n'
                        text += text_sentence
                        done = True
        return text

text = open(sys.argv[1]).read()
paragraphs = text.split('\n')
test = Ngram_model(paragraphs,3)
print test.generate_new_text(int(sys.argv[2]))
