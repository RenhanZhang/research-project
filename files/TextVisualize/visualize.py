import matplotlib
matplotlib.use('Agg')
from datetime import datetime, timedelta
from TextProcess import preprocess
import operator
from matplotlib import pyplot as plt

import ipdb
import StringIO
import urllib, base64

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

    print freq_words
    for word in freq_words:

        counts = []
        for date in dates:
            counts.append(post_dict[date].get(word, 0))

        # updating max_occurence
        max_occurence = max_occurence if max_occurence > max(counts) else max(counts)
        plt.plot_date(dates, counts, linestyle='-')

    fig = plt.gcf()
    fig.set_size_inches(18.5, 10.5)

    # set the x axis to [one day before the earliest, one day after the latest]
    # set y axis to [0, max word count]
    buffer = timedelta(days=2)
    plt.axis([min(dates) - buffer, max(dates) + buffer, 0,  int(1.2 * max_occurence)])
    plt.legend(freq_words, loc='upper left')
    #plt.savefig('/home/rhzhang/wf_vs_time.png')
    #plt.savefig('/home/rhzhang/public_html/research-project/files/media/wf_vs_time.png')
    
    fig = plt.gcf()
    fig.set_size_inches(18.5, 10.5)

    imgdata = StringIO.StringIO()
    fig.savefig(imgdata, format='png')
    print "Content-Type: image/png\n"
    imgdata.seek(0)  # rewind the data

    uri = urllib.quote(base64.b64encode(imgdata.buf))
    return uri
