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
import re, os, errno
from wordcloud import WordCloud
def words_vs_time(posts, freq_words=[]):
    '''
    :param posts: a list of posts
    :param freq_words: a list of frequent words that are to be plotted against time.
                       If not provided, the most frequent 5 words across all blogs are used
    :return:
    '''

    post_dict = {}  # key: datetime object, val: word count dict of the content of the blog
    freq_words_provided = len(freq_words) > 0
    global_word_count = {}   # the word frequency across the collections
    for post in posts:
        date = datetime(post['pub_year'], post['pub_month'], post['pub_day'])
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
    # ipdb.set_trace()
    # maintain max_occurence for setting y axis of the plot
    max_occurence = 0
    colors = ['r', 'g', 'b', 'y', 'c', 'm', 'k']
    
   
    for (word, color) in zip(freq_words, colors):
        counts = []
        for date in dates:
            counts.append(post_dict[date].get(word, 0))

        # updating max_occurence
        max_occurence = max_occurence if max_occurence > max(counts) else max(counts)
        plt.plot_date(dates, counts, linestyle='-', c=color)
    
    fig = plt.gcf()
    fig.set_size_inches(18.5, 10.5)
    # set the x axis to [one day before the earliest, one day after the latest]
    # set y axis to [0, max word count]
    buffer = timedelta(days=2)
    plt.axis([min(dates) - buffer, max(dates) + buffer, 0,  int(1.2 * max_occurence)])
    plt.legend(freq_words, loc='upper left')

    imgdata = StringIO.StringIO()
    fig.savefig(imgdata, format='png')
    # print "Content-Type: image/png\n"
    imgdata.seek(0)  # rewind the data
    plt.close()
    uri = urllib.quote(base64.b64encode(imgdata.buf))
    return uri

def ling_ethnography(posts):
    dict_fname = 'LinguisticEthnography/GeneralInquirer/GeneralInquirer.all.txt'
    class_scores = {}  # store the dominance score of semantic classes of every post

    for post in posts:
        if len(post['content']) < 100:
            continue
        temp_id = str(uuid.uuid4())
        result_fname = 'result_%s.txt' %temp_id
        post_fname = 'post_%s.txt' %temp_id
        with open(post_fname, 'wb') as f:
            f.write(post['content'])
        with open(result_fname, 'wb') as f:
            # use the package and output the result to file result_temp_id.txt
            cmd = "perl LinguisticEthnography/EthnolingClasses.pl -fg %s -bg bg_corpus.txt -dict %s >%s" %(post_fname, dict_fname, result_fname)
            print cmd
            subprocess.call(cmd, shell=True)

        # load the results
        class_score = []
        with open(result_fname, 'rb') as f:

            for line in f.readlines():
                pattern = '(\w+)\s(\d+\.\d+)'
                match = re.search(pattern, line)
                if match:
                    class_name = match.group(1)
                    score = float(match.group(2))
                    class_score.append((class_name, score))

            class_score = sorted(class_score, key=lambda x:x[1])

        class_scores[post['title']] = class_score

        # remove these temp file
        silentremove(result_fname)
        silentremove(post_fname)

    return class_scores

def silentremove(filename):
    try:
        os.remove(filename)
    except OSError as e: # this would be "except OSError, e:" before Python 2.6
        if e.errno != errno.ENOENT: # errno.ENOENT = no such file or directory
            raise # re-raise exception if a different error occured

def word_cloud(posts):
    text = ' '.join(post['content'] + ' ' + post['title'] for post in posts)
    wordcloud = WordCloud(background_color="white", max_words=2000, width=1200, height=900)
    wordcloud.generate(text)
    fig = plt.gcf()
    # fig.set_size_inches(15, 8.5)
    # Open a plot of the generated image.
    plt.imshow(wordcloud)
    plt.axis("off")

    imgdata = StringIO.StringIO()
    fig.savefig(imgdata, format='png')
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

    post_dict = {}  # key: datetime object, val: word count dict of the content of the blog
    freq_words_provided = len(freq_words) > 0
    global_word_count = {}   # the word frequency across the collections
    # ipdb.set_trace()
    for post in posts:
        date = datetime(post['pub_year'], post['pub_month'], post['pub_day'])
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

    #ipdb.set_trace()
    table = u"['Date'"
    for word in freq_words:
        table += u", '%s'" %word
    table += u']'

    for date in dates:
        s = u",\n        ['{year}-{month}-{day}'".format(year=date.year, month=date.month, day=date.day)
        for word in freq_words:
            s += u', %s' %post_dict[date].get(word, 0)
        s += u']'

        table += s

    return table








