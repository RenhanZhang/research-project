import matplotlib
matplotlib.use('Agg')
from datetime import datetime, timedelta
from TextProcess import preprocess
import operator
from matplotlib import pyplot as plt
import subprocess
import ipdb
import StringIO
import urllib, base64
import uuid
import re, os, errno, codecs
from wordcloud import WordCloud
import json
from time import mktime

dirname = os.path.dirname(os.path.abspath(__file__))

def ling_ethnography(posts):
    package_dir = dirname + '/LinguisticEthnography/'
    N = 5
    dict_fname = package_dir + 'LIWC/LIWC.all.txt'

    contents = ' '.join([(post['content'] + ' ' + post['title']) for post in posts])
    
    temp_id = str(uuid.uuid4())
    result_fname = dirname + '/result_%s.txt' %temp_id
    contents_fname = dirname + '/contents_%s.txt' %temp_id
    with codecs.open(contents_fname, 'wb', encoding='utf8') as f:
        f.write(contents)

    cmd = "perl {EthnolingClasses} -fg {fg} -bg {bg} -dict {dict} >{result}"\
              .format(EthnolingClasses=package_dir+'EthnolingClasses.pl', fg=contents_fname, bg=package_dir+'bg_corpus.txt',\
                      dict=dict_fname, result=result_fname)


    subprocess.call(cmd, shell=True)

    # load the results
    class_score = []
    with codecs.open(result_fname, 'rb', encoding='utf8') as f:
        for line in f.readlines():
            pattern = '(\w+)\s(\d+\.\d+)'
            match = re.search(pattern, line)
            if match:
                class_name = match.group(1)
                score = float(match.group(2))
                class_score.append((class_name, score))

    # ipdb.set_trace()
    # sort class_score and take the top N classes
    class_score = sorted(class_score, key=lambda x:x[1], reverse=True)

    # remove these temp file
    silentremove(result_fname)
    silentremove(contents_fname)

    # make sense of the class

    # load the class explanation file into a dictionary
    dic = {}
    with codecs.open(package_dir+'LIWC/liwc_exp.txt', 'r') as f:
        for line in f.readlines():
            l = line.split(':')
            dic[l[0].lower()] = l[1].rstrip()

    result = []
    count = 0
    for cls, score in class_score:
        if count > N:
            break
        if cls.lower() in dic:
            count += 1
            result.append(dic[cls.lower()].lower())

    return result


def silentremove(filename):
    try:
        os.remove(filename)
    except OSError as e: # this would be "except OSError, e:" before Python 2.6
        if e.errno != errno.ENOENT: # errno.ENOENT = no such file or directory
            raise # re-raise exception if a different error occured

def word_cloud(posts):
    text = ' '.join(post['content'] + ' ' + post['title'] for post in posts)
    wordcloud = WordCloud(background_color="white", width=1200, height=900, margin=0)
    wordcloud.generate(text)
    fig = plt.gcf()
    # fig.set_size_inches(15, 8.5)
    # Open a plot of the generated image.
    plt.imshow(wordcloud)
    plt.axis("off")

    imgdata = StringIO.StringIO()
    fig.savefig(imgdata, format='png', bbox_inches='tight')
    imgdata.seek(0)  # rewind the data
    plt.close()
    uri = urllib.quote(base64.b64encode(imgdata.buf))
    return uri

def words_vs_time_beta(posts, freq_words=[]):
    '''
    :param posts: a list of posts
    :param freq_words: a list of frequent words that are to be plotted against time.
                       If not provided, the most frequent 5 words across all blogs are used
    :return:
    '''

    post_dict = {}  # key: datetime object, val: word count dict of the content of the post
    freq_words_provided = len(freq_words) > 0
    global_word_count = {}   # the word frequency across the collections
    # ipdb.set_trace()
    for post in posts:
        date = datetime.fromtimestamp(post['published']/1000)
        word_count = preprocess.preprocess(post['content'])

        # need to deal with the case where more than one posts are published on the same day

        if date in post_dict:
            existing_dict = post_dict[date]
            for word in word_count:
                existing_dict[word] = existing_dict.get(word, 0) + word_count[word]
        else:
            post_dict[date] = word_count

        # compute the word frequency across the collections
        if not freq_words_provided:
            for word in word_count:
                global_word_count[word] = global_word_count.get(word, 0) + word_count[word]

    if not freq_words_provided:
        sorted_list = sorted(global_word_count.items(), key=operator.itemgetter(1), reverse=True)
        freq_words = [x[0] for x in sorted_list[:5]]

    dates = sorted(post_dict.keys())

    header = ['Date']
    header.extend(freq_words)
    table = [header]

    for date in dates:
        row = ['%s-%s-%s'%(date.year, date.month, date.day)]
        for word in freq_words:
            row.append(post_dict[date].get(word, 0))
        table.append(row)


    return json.dumps(table)

def ngram_model(posts, N=3):

    text = ' '.join([post['content'] for post in posts])
    temp_id = str(uuid.uuid4())
    contents_fname = dirname + '/contents_%s.txt' %temp_id
    with codecs.open(contents_fname, 'wb', encoding='utf8') as f:
        f.write(text)
    model = subprocess.check_output(['python', dirname+'/'+'ngram_model.py', contents_fname, str(N)])

    silentremove(contents_fname)
    return model





