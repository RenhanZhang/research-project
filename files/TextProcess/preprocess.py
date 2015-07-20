from nltk.corpus import stopwords
from collections import Counter

def rm_stopwords(s):
    '''
    remove stopwords as listed in nltk.corpus.stopwords
    :param s: an input of string)
    :return: a string with stopwords removed, and the other words are in the same ordering as before
    '''

    sw = stopwords.words("english")
    return ' '.join([word for word in s.split() if word not in sw])


def word_freq(s):
    '''
    :param s: a string
    :return:  a dictionary, key being a word that showing up in s, value being its counts
    '''
    return Counter(s.split())

def rm_space(s):
    return ' '.join(s.split())
