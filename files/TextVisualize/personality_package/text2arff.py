#! /usr/bin/python

#
# Script used to extract mrc and liwc features from generic text
# Uses features.py
# Code based on extract_features.py
#
# Steve Wilson
# Summer 2015
#

import sys
import features
import os
dirname = os.path.dirname(os.path.abspath(__file__))

# any new extractors should not have features by the same name as current set
# otherwise, values will be overwritten
def text2feat_dict(text, extractors):
    features = {}
    for ename,extr in extractors.items():
        features.update(extr.extract_from(text))
    return features

# convert dictionary to arff format
# returns a string containing the contents of the arff
def dict2arff(d, target_name):
    arff = ""
    arff += "@relation " + target_name + '\n\n'
    keys = sorted(list(d.keys()))
    for key in keys:
        arff += "@attribute " + key + " numeric\n"
    arff += "@attribute " + target_name + " numeric\n\n"
    arff += "@data\n\n"
    arff += ','.join([str(d[key]) for key in keys]) + ',?'
    return arff

# text is the text to extract features from
# target name is the name of the target attribute to predict
# wordlist (optional) is a list of unigrams to use a features (fequency counts)
# returns dictionary where keys are feature names and values are features
# targets should be one of: [ope, con, agr, neu, ext]
def extract_from(text, target_name='target', wordlist=None):
# Change here to use different feature sets
    FEATURES_TO_USE = {
        'LIWC': features.LexiconFeatureExtractor(dirname+'/resources/lexicons/LIWC.all.txt'),
        'MRC': features.DatabaseFeatureExtractor(dirname+'/resources/mrc/Word_data.csv',['WORD','WTYPE']),
        'Unigram': features.WordListExtractor(wordlist),
        'Basic': features.SimpleCountExtractor()
    }
    result = text2feat_dict(text, FEATURES_TO_USE)
    return dict2arff(result, target_name)

# testing
if __name__ == "__main__":
    if len(sys.argv) < 1:
        sys.stderr.write("Usage: ./text2arff.py <textfile>")
    else:
        arff = extract_from(open(sys.argv[1]).read()) # argv[1] should be filename to read text from
        print arff
        sys.stderr.write("NOTE: need to change the 'target' variable name to one of: [ope, con, agr, neu, ext] depending on model to use")
