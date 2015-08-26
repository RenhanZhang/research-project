
#
# features.py
# tools and data structures for extrating psycholinguistic features
#
# Steve Wilson
# Winter 2015
#

import collections
import csv
import re

import nltk

# All POS tags used by MRC database
ALL_POS = 'NVPJARCUIO'

# Require WORD_LIMIT words per text sample
WORD_LIMIT = 50

# Convert treebank style POS tags to those used in MRC
def simple_pos(treebank_pos):
    # Noun
    if treebank_pos[0]=='N':
        return 'N'
    # Past Participle
    elif treebank_pos=="VBN":
        return 'P'
    # Verb
    elif treebank_pos[0]=='V':
        return 'V'
    # Adjective
    elif treebank_pos[0]=='J':
        return 'J'
    # Adverb
    elif treebank_pos[:2]=="RB":
        return 'A'
    # Preposition
    elif treebank_pos=="IN":
        return 'R'
    # Conjunction
    elif treebank_pos=="CC":
        return 'C'
    # Pronoun
    elif treebank_pos[:3]=="PRP" or treebank_pos[:2]=="WP":
        return 'U'
    # Interjection
    elif treebank_pos=="UH":
        return 'I'
    # Other
    else:
        return 'O'


# custom \b that will include the ' character as part of words and split on 10th to get 10 and th (this is what LIWC does)
B = r"(?:(?<=\d)(?=[a-zA-Z])|(?<=[\w'])(?![\w'])|(?<![\w'])(?=[\w']))"

# most abstract class for feature extractors
class FeatureExtractor(object):
    def __init__(self):
        pass

# class to handle generic LIWC features that don't appear in the lexicon
class SimpleCountExtractor(FeatureExtractor):

    anyword_pattern = re.compile(B + r"[\w']+?" + B)

    def __init__(self):
        self.patterns = {
            'ALLPCT' : re.compile(r""",|\.|;|:|"|-|!|\?|\(|\)|_|/|\\|'|@|#|\$|%|\^|&|\*|\[|\]"""),
            'APOSTRO' : re.compile(r"'"),
            'COMMA' : re.compile(r","),
            'COLON' : re.compile(r":"),
            'DASH' : re.compile(r"-"),
            'EXCLAIM' : re.compile(r"!"),
            'OTHERP' : re.compile(r"@|#|\$|%|\^|&|\*|\[|\]|/|\\"),
            "PARENTH" : re.compile(r"\(|\)"),
            "PERIOD" : re.compile(r"\."),
            "QMARK" : re.compile(r"\?"),
            "QUOTE" : re.compile(r'"'),
            "SEMIC" : re.compile(r';'),
            "SIXLTR" : re.compile(B+ r'\w{7,}' + B)
        }

    def extract_from(self,text):
        # using text.lower() so that when moving to set() will ignore capitalization
        allwords = re.findall(self.anyword_pattern,text.lower())
        numwords = len(allwords)
        if numwords < WORD_LIMIT:
            print text
            return {}
        res = {'LIWC_'+pattern_name:100*float(len(re.findall(pattern,text)))/numwords for pattern_name,pattern in self.patterns.items()}
        res['LIWC_WC'] = len(allwords)
        res['LIWC_UNIQUE'] = 100*float(len(set(allwords)))/numwords
        wps_counts = []
        for sent in nltk.sent_tokenize(text):
            wps_counts.append(len(re.findall(self.anyword_pattern,sent)))
        res['LIWC_WPS'] = float(sum(wps_counts))/len(wps_counts)
        return res

# used with topkwords output
class WordListExtractor(FeatureExtractor):

    anyword_pattern = re.compile(r"\b[\w]+?\b")

    def __init__(self,wordlist_path):
        if wordlist_path:
            self.words = [x.strip() for x in open(wordlist_path).readlines()]
        else:
            self.words = None

    def extract_from(self,text):
        res = {}
        if self.words:
            allwords = re.findall(self.anyword_pattern,text.lower())
            numwords = len(allwords)
            if numwords < WORD_LIMIT:
                return {}
            res = {}
            for i,word in enumerate(self.words):
                res['UNI_'+str(i)+'_'+word.upper()] = float(allwords.count(word))/numwords
        return res

# to be used with LIWC or other lexicon
class LexiconFeatureExtractor(FeatureExtractor):

    anyword_pattern = re.compile(B + r"[\w']+?" + B)

    def __init__(self,lexicon_path,lexicon_format=None):
        # setting a default lexicon format if not given
        # this is what LIWC uses
        if not lexicon_format:
            # looking for <pattern> ,<category> on each line
            # e.g., alarm* ,AFFECT
            lexicon_format = re.compile("(?P<pattern>[\w'-]+\*?)\s*,\s*(?P<category>\w+)")
        self.lexicon = self._load_lexicon(lexicon_path,lexicon_format)

    def _load_lexicon(self,lexicon_path,lexicon_format):
        l = {}
        l2 = collections.defaultdict(list)
        with open(lexicon_path) as lex_file:
            for line in lex_file.readlines():
                m = re.match(lexicon_format,line)
                if m:
                    entry = m.groupdict()
                    # convert something like "alarm*" to "\balarm\w+\b" as a regex
#                    regex = re.compile(B + entry['pattern'].replace("*",r'\w*') + B,re.I)
#                    l[regex] = entry['category']
                    l2[entry['category']].append(entry['pattern'].replace("*",r"[\w']*"))
                else:
                    sys.stderr.write("WARNING: Did not match line in lexicon:"+str(line)+'\n')
        return l2

    def extract_from(self,text):
        counts = collections.defaultdict(int)
        allwords = re.findall(self.anyword_pattern,text)
        numwords = len(allwords)
        if numwords < WORD_LIMIT:
            return {}
        foundwords = set([])
#        print allwords
#        print "numwords:",numwords

        for category,patterns in self.lexicon.items():
            regex = re.compile(B + '(' + '|'.join(patterns) +')' + B,re.I)
            matches = re.findall(regex,text)

##       for pattern,category in self.lexicon.items():
##            matches = re.findall(pattern,text)
            count = len(matches)
            # important: normalize by number of words
            # rounding to try to get the same results as paper,
            # not because it is necessary
            counts['LIWC_'+category] += 100 * (float(count)/numwords)
            for word in matches:
                foundwords.add(word)
        numfound = 0
        for word in allwords:
            if word in foundwords:
                numfound += 1
        counts['LIWC_DIC'] = 100*float(numfound)/numwords
        return counts

# treat as abc
class WordLevelFeatureExtractor(FeatureExtractor):

    anyword_pattern = re.compile(B + r"[\w']+?" + B)

    # average means that we will take the average score for all
    # words that were found in the database
    def __init__(self,average=True):
        # must define this function in derived class
        self.word_level_extractor = None
        # take the average instead of total count
        self.average = average
        # this can switch if we average over all words found in database or just nonzero valued words for a given feature
        self.excluding_zeros = True

    def extract_from(self,text):
        n = collections.defaultdict(int)
        n_stat = 0
        results = collections.defaultdict(float)
        allwords = re.findall(self.anyword_pattern,text)
        if len(allwords) < WORD_LIMIT:
            return {}
        for word_pos_pair in nltk.pos_tag(allwords):
            word, pos = word_pos_pair
            for key,value in self.word_level_extractor((word.upper(),simple_pos(pos))).items():
                key = 'MRC_'+key
                # only want to use numeric features; this should work for those
                try:
                    fv = float(value)
                # couldn't convert to a float, don't use this feature
                except:
                    pass
                # do this if 'try' was successful - now know that float(value) conversion worked
                else:
                    if fv!=0:
                        results[key] += fv
                        n[key] += 1
                        n_stat += 1
        if self.average:
            if self.excluding_zeros:
                results = {k:float(v)/n[k] for k,v in results.items()}
            else:
                results = {k:float(v)/n_stat for k,v in results.items()}
        return results

# to be used with MRC or other csv lookup table
# later will need to select features of interest, since this may give too many
class DatabaseFeatureExtractor(WordLevelFeatureExtractor):

    # database should be converted to CSV
    # for MRC, set keys = [word,wtype]
    def __init__(self,database_path,keys,average=True):
        super(DatabaseFeatureExtractor,self).__init__(average)
        self.database = self._load_database(database_path,keys)
        self.word_level_extractor = self._lookup

    # if word wasn't found with that pos, try to find the word with another pos and return the entry for the most common pos based on k-f-freq
    def retry_variations(self,key):
        word,pos = key
        best = {}
        for newpos in ALL_POS:
            newkey = (word,newpos)
            if newkey in self.database:
                if not best:
                    best = self.database[newkey]
                else:
                    if self.database[newkey]['K-F-FREQ'] > best['K-F-FREQ']:
                        best = self.database[newkey]
        return best

    def _load_database(self,path,keys):
        db = {}
        with open(path) as database_file:
            reader = csv.DictReader(database_file)
            for line in reader:
                key = []
                for k in keys:
                    if '|' in k:
                        k = k.split('|')[0]
                    key.append(line.pop(k))
                if tuple(key) not in db:
                    db[tuple(key)] = line
                else:
                    line2 = db[tuple(key)]
                    for k,v in line2.items():
                        try:
                            if float(v)==0:
                                db[tuple(key)][k] = line2[k]
                            else:
                                if float(line2[k])!=0 and float(line2[k])!=float(v):
                                    print "WARNING: Entries don't match:",k
                        except:
                            pass
        return db

    def _lookup(self,key):
        if key in self.database:
#            print "found:",key
#            print self.database[key]
            return self.database[key]
        else:
            # do this so that calling .items() doesn't fail
#            print "not found:",key
            return self.retry_variations(key)
