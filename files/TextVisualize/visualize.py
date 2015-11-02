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
from GChartWrapper import Radar
from stanford_corenlp_pywrapper import CoreNLP

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
    text = u' '.join(post['content'] for post in posts)
    
    '''
    if os.path.isdir('/home/public/stanford-corenlp-full-2015-04-20/'):
        proc = CoreNLP("pos", corenlp_jars=["/home/public/stanford-corenlp-full-2015-04-20/*"])
        sentenses = proc.parse_doc(text)['sentences']
        
        text = ''

        for sentence in sentenses:
            text += u' '.join(sentence['lemmas']) + u' '
    '''

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
    
def words_vs_time(posts, freq_words=[], group_by='month'):
    '''
        similar to words_vs_time_beta, only difference is to group the posts in months
    '''

    post_dict = {}  # key: datetime object, val: word count dict of the content of the post
    freq_words_provided = len(freq_words) > 0
    global_word_count = {}   # the word frequency across the collections
    # ipdb.set_trace()
    for post in posts:
        date = datetime.fromtimestamp(post['published']/1000)

        if group_by == 'year':
            key = str(date.year)
        elif group_by == 'month':
            key = '%s-%s' % (date.year, date.month)
        elif group_by == 'week':
            key = '%s-%s' % (date.year, date.isocalendar()[1])
        else:
            key = '%s-%s-%s' % (date.year, date.month, date.day)

        word_count = preprocess.preprocess(post['content'])

        # need to deal with the case where more than one posts are published on the same day

        if key in post_dict:
            existing_dict = post_dict[key]
            for word in word_count:
                existing_dict[word] = existing_dict.get(word, 0) + word_count[word]
        else:
            post_dict[key] = word_count

        # compute the word frequency across the collections
        if not freq_words_provided:
            for word in word_count:
                global_word_count[word] = global_word_count.get(word, 0) + word_count[word]

    if not freq_words_provided:
        sorted_list = sorted(global_word_count.items(), key=operator.itemgetter(1), reverse=True)
        freq_words = [x[0] for x in sorted_list[:5]]

    keys = sorted(post_dict.keys())

    header = ['Month']
    header.extend(freq_words)
    table = [header]

    for key in keys:
        row = [key]
        for word in freq_words:
            row.append(post_dict[key].get(word, 0))
        table.append(row)

    return json.dumps(table)

def ngram_model(posts, N=3):

    text = ' '.join([post['content'] for post in posts])
    temp_id = str(uuid.uuid4())
    contents_fname = dirname + '/contents_%s.txt' % temp_id
    with codecs.open(contents_fname, 'wb', encoding='utf8') as f:
        f.write(text)
    model = subprocess.check_output(['python', dirname+'/'+'ngram_model.py', contents_fname, str(N)])

    silentremove(contents_fname)
    return model

def compute_personality(posts):
    # ipdb.set_trace()
    print 'personality'
    pkg_path = dirname + '/personality_package'
    weka_path = dirname + '/weka-3-7-12/weka.jar'
    traits = ['con', 'ope', 'neu', 'agr', 'ext']
    text = ' '.join([post['content'].encode('ascii', errors='ignore') for post in posts])
    temp_id = str(uuid.uuid4())
    scores = []         # store the scores of different personality traits
    abbrev = {
        'con': 'conscientiousness', 'ope': 'openness', 'neu': 'emotional-stability', 
        'agr': 'agreeableness', 'ext': 'extraversion', 
    }

    cont_path = pkg_path + '/content%s.txt' % temp_id
    # write the text to cont_path
    with codecs.open(cont_path, 'wb', encoding='utf8') as f:
        f.write(text)
        # prepare the arff data for prediction
        try:
            arff_data = subprocess.check_output(['python', pkg_path + '/text2arff.py', cont_path],
                                             stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            raise RuntimeError("command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output))

    # remove the content file as we have the arff file now
    silentremove(cont_path)

    for trait in traits:
        print trait
        arff = arff_data.replace('target', trait)

        arff_path = pkg_path + '/' + temp_id + trait + '.arff'
        with codecs.open(arff_path, 'wb', encoding='utf8') as f:
            f.write(arff)

        cmd = ['bash', pkg_path + '/predict.sh', weka_path, 'functions.LinearRegression', 
               arff_path,pkg_path + '/models/%s.linear-regression.model' % abbrev[trait]]

        try:
            result = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            raise RuntimeError("command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output))
        silentremove(arff_path)

        score = float(result.split()[-2])
        scores.append(score)
    
    # ensure scores are in (0,5) range
    scores = [min(5, x) for x in scores]
    scores = [max(0, x) for x in scores]
    
    # convert emotional unstability to stability
    avg = [3.48682181564, 3.78697472093, 2.77373519534, 3.5433602257, 3.57498918951]
    scores[2] = 2 * avg[2] - scores[2]
    
    return scores


def get_personality(profile_url, posts, dbh):
    
    # step 1: try to get the big_5 scores inferred from the blog posts
    #         this information can be already computed and stored in the db 
    stmt = 'select conscientiousness, openness, neuroticism, agreeableness, extraversion from big_5_from_blogs where profile_url = %s;'
    
    result = dbh.exec_and_get(stmt, [profile_url])

    if result:
        scores_from_blogs = list(result[0])
    else:
        # if it's not in the db, compute it and add it to the db
        scores_from_blogs = compute_personality(posts) 
        
        stmt = '''
               insert into big_5_from_blogs (profile_url, conscientiousness, openness, neuroticism, agreeableness, extraversion)
               values(%s, %s, %s, %s, %s, %s);
               '''
        params = [profile_url]
        params.extend(scores_from_blogs)

        dbh.exec_and_get(stmt, params) 
    
    # step 2: get the personality score obstained from the surveys in the db
    scores_from_survey = None
    # ipdb.set_trace()
    stmt = 'select conscientiousness, openness, neuroticism, agreeableness, extraversion from big_5_from_survey where profile_url = %s;'

    result = dbh.exec_and_get(stmt, [profile_url])

    if result:
        scores_from_survey = list(result[0])

    # step 3: draw the chart
    avg = [3.48682181564, 3.78697472093, 2.77373519534, 3.5433602257, 3.57498918951]

    # add an extra term so tail meets head in the radar chart
    scores_from_blogs.append(scores_from_blogs[0])
    avg.append(avg[0])
    data = [scores_from_blogs, avg]

    if scores_from_survey:
        # assert 1==2
        scores_from_survey.append(scores_from_survey[0])
        data.append(scores_from_survey)

    G = Radar(data, encoding='text')  
    G.title('5-Traits Personality')
    G.type('rs')
    G.size(540,540)
    G.color('blue','CC3366')
    G.line(2,1,0)
    G.line(2,1,0)
    G.axes(['y', 'x'])
    G.axes.range(0, 0, 5, 1)
    G.label(1, 2, 3, 4, 5)
    name = 'You'
    if 'author' in posts[0] and 'displayName' in posts[0]['author']:
        name = posts[0]['author']['displayName']

    if scores_from_survey:
        G.legend('from blogs', 'Average', 'from the survey')
        G.color('blue', 'CC3366', 'black')
    else:
        G.legend('from blogs', 'Average')

    G.label('conscientious', 'open', 'emotional-stable', 'agreeable', 'extraverse')

    max_score = max(scores_from_blogs)
    if scores_from_survey:
        max_score = max(max_score, max(scores_from_survey))
    G.scale(0,max_score)

    G.margin(10, 10, 10, 0)
    #G.url += '&chdlp=b'
    return G.url + '&chxs=0,989898,12|1,000000,12,0'

'''
def peronality(posts):
    # ipdb.set_trace()
    print 'personality'
    pkg_path = dirname + '/personality_package'
    weka_path = dirname + '/weka-3-7-12/weka.jar'
    traits = ['con', 'ope', 'neu', 'agr', 'ext']
    text = ' '.join([post['content'].encode('ascii', errors='ignore') for post in posts])
    temp_id = str(uuid.uuid4())
    scores = []         # store the scores of different personality traits
    abbrev = {
        'con': 'conscientiousness', 'ope': 'openness', 'neu': 'emotional-stability', 
        'agr': 'agreeableness', 'ext': 'extraversion', 
    }

    cont_path = pkg_path + '/content%s.txt' % temp_id
    # write the text to cont_path
    with codecs.open(cont_path, 'wb', encoding='utf8') as f:
        f.write(text)
        # prepare the arff data for prediction
        try:
            arff_data = subprocess.check_output(['python', pkg_path + '/text2arff.py', cont_path],
                                             stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            raise RuntimeError("command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output))

    # remove the content file as we have the arff file now
    # silentremove(cont_path)

    for trait in traits:
        print trait
        arff = arff_data.replace('target', trait)

        arff_path = pkg_path + '/' + temp_id + trait + '.arff'
        with codecs.open(arff_path, 'wb', encoding='utf8') as f:
            f.write(arff)

        cmd = ['bash', pkg_path + '/predict.sh', weka_path, 'functions.LinearRegression', 
               arff_path,pkg_path + '/models/%s.linear-regression.model' % abbrev[trait]]

        try:
            result = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            raise RuntimeError("command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output))
        # silentremove(arff_path)

        score = float(result.split()[-2])
        scores.append(score)
    

    avg = [3.48682181564, 3.78697472093, 2.77373519534, 3.5433602257, 3.57498918951]

    # ensure scores are in (0,5) range
    scores = [min(5, x) for x in scores]
    scores = [max(0, x) for x in scores]

    # add an extra term so tail meets head in the radar chart
    scores.append(scores[0])
    avg.append(avg[0])

    # convert emotional unstability to stability
    scores[2] = 2 * avg[2] - scores[2]

    print scores
    print avg

    G = Radar([scores, avg], encoding='text')  
    G.title('5-Traits Personality')
    G.type('rs')
    G.size(500,500)
    G.color('blue','CC3366')
    G.line(2,1,0)
    G.line(2,1,0)
    G.axes(['y', 'x'])
    G.axes.range(0, 0, 5, 1)
    G.label(1, 2, 3, 4, 5)
    name = 'You'
    if 'author' in posts[0] and 'displayName' in posts[0]['author']:
        name = posts[0]['author']['displayName']
    G.legend('You', 'Average')
    G.label('conscientious', 'open', 'emotional-stable', 'agreeable', 'extraverse')
    G.scale(0,max(scores))
    G.margin(10, 10, 10, 0)
    #G.url += '&chdlp=b'
    return G.url + '&chxs=0,989898,12|1,000000,12,0'
'''


if __name__ == '__main__':
    print 'visualize module'






