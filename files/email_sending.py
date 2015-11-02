import re, os, smtplib, datetime, string, random, datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from bs4 import BeautifulSoup 
from TextVisualize import visualize
from DB_Handling import BlogsDB
import random
from Blogger_Retriever import get
import ipdb
import re, os
import multiprocessing as mp
from Qualtrics import qualtrics_get

dirname = os.path.dirname(os.path.abspath(__file__))

with open(dirname+'/emails/email_account.txt', 'r') as f:
    username = f.readline().split()[1]
    pwd = f.readline().split()[1]

MIN_NUM_WORD = 1000

def partial_result(blog_link):
    dbh = BlogsDB.BlogsDB_Handler()
    MAX_TO_DISPLAY = 100

    posts = dbh.get_posts_in_blog(blog_link)

    # ipdb.set_trace()
    if len(posts) == 0:
        latest = -1
    else:
        latest = posts[-1]['published']

    profile, blog, new_posts, next_page_token = get.get_blog_by_link(blog_link, latest, MAX_TO_DISPLAY)

    if blog is None:
        return {}
    
    # if profile and 'url' in profile and 'image_url' not in profile:
        # save profile and its blogs when failing to scrape it right now
        # save_profile(profile['url'], blog['url'])

    posts.extend(new_posts)

    if len(posts) == 0:
        return {}
    
    '''
    mask = MAX_TO_DISPLAY if len(posts) > MAX_TO_DISPLAY else len(posts)
    ctx = {'blog_name': blog['name'].replace("\'", '')}
    # visualization
    ctx['wf_vs_month'] = visualize.words_vs_time(posts=posts[-mask:], freq_words=[], group_by='month')
    ctx['wf_vs_year'] = visualize.words_vs_time(posts=posts[-mask:], freq_words=[], group_by='year')
    ctx['wf_vs_week'] = visualize.words_vs_time(posts=posts[-mask:], freq_words=[], group_by='week')
    ctx['wf_vs_day'] = visualize.words_vs_time(posts=posts[-mask:], freq_words=[], group_by='day')
    ctx['word_cloud'] = visualize.word_cloud(posts[-mask:])
    '''

    # update the database
    dbh.batch_update(profile, blog, new_posts)

    # spawn a parallel process the retrieve the remaining posts
    if next_page_token:
        proc = mp.Process(target=get.get_remain_posts,
                          args=(blog_link, blog['id'], next_page_token, get.MAX_TO_DISPLAY - len(posts), latest))
        proc.start()

    dbh.close()
    return posts


def send_email(recepient, contents={}):
    
    # Create message container - the correct MIME type is multipart/alternative.
    msg = MIMEMultipart('alternative')
    msg['Subject'] = "Testing"
    msg['From'] = username
    msg['To'] = recepient

    # load the html body
    with open(dirname + '/emails/email_embedded.html', 'r') as f:
        html = f.read()

    html = html.format(blog_name=contents['blog_name'],
                       surveys_taken=contents['surveys_taken'],
                       token=contents['id'],
                       )
    html = re.sub('{word_cloud}', contents['word_cloud'], html)

    '''
    with open(str(datetime.datetime.now())+'.html', 'w') as f:
        f.write(html)
    '''
    
    html_msg = MIMEText(html, 'html')
    plain_msg = MIMEText(html, 'plain')
    msg.attach(html_msg)
    # msg.attach(plain_msg)
    # Send the message via local SMTP server.
    server = smtplib.SMTP('smtp.gmail.com:587')
    server.ehlo()
    server.starttls()
    server.login(username,pwd)
    server.sendmail(username, recepient, msg.as_string())
    server.quit()
    
# this function get token from the db if any
# otherwise it will generate one, update the db and return the newly-generated token
def get_token(profile_url, length=10):

    dbh = BlogsDB.BlogsDB_Handler()

    # check if the db has the user in the table
    cmd = '''
             select token from profiles_tokens
             where profile_url = %s;
          '''
    result = dbh.exec_and_get(cmd, [profile_url])
    assert len(result) <= 1   # there should be at most one entry in the table of profile_url
    if len(result) == 1:
        return result[0][0]

    # else create a new one and update the db
    alphabet = "abcdefghijklmnopqrstuvwxyz0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"

    # generate a token that hasn't been created
    while True:
        token = ""
        for i in range(length):
             token += alphabet[random.randrange(len(alphabet))]
        
        # ensure this token has not been used by other users
        cmd = '''
                  select profile_url 
                  from profiles_tokens 
                  where token = %s;
              '''
        if len(dbh.exec_and_get(cmd, [token])) == 0:
            break

    # update the profiles_tokens table
    cmd = 'insert into profiles_tokens(profile_url, token) value(%s, %s);'
    dbh.exec_stmt(cmd, [profile_url, token])

    return token

def invite():
    dbh1 = BlogsDB.BlogsDB_Handler()  # used to get all the valid profiles and necessary info

    ''' select profiles that 
        1) has an email
        2) has not been considered as invalid (with too few words)
        3) has not been sent an email
    '''
    cmd = '''
          select p.url, p.email, pb.blog_url, blogs.name 
          from profiles as p, profiles_blogs as pb, blogs 
          where p.url = pb.profile_url 
          and pb.blog_url = blogs.url
          and p.email is not null
          and p.url not in (select url from invalid_profiles) 
          and p.url not in (select profile_url from profiles_tokens)
          limit 5;
          '''
    cmd = '''
          select p.url, p.email, pb.blog_url, blogs.name 
          from profiles as p, profiles_blogs as pb, blogs 
          where p.url = pb.profile_url 
          and pb.blog_url = blogs.url
          and p.url = 'http://www.blogger.com/profile/00420783423172718178';
          '''
    

    #ipdb.set_trace()
    profiles_detail = {} 

    for e in dbh1.exec_and_get(stmt=cmd, params=[]):
        profile_url = e[0]
        email = e[1]
        blog_url = e[2]
        blog_name = e[3]

        if profile_url not in profiles_detail:
            profiles_detail[profile_url] = {}

        profiles_detail[profile_url]['email'] = email
        profiles_detail[profile_url]['name'] = blog_name

        if 'blog_posts' not in profiles_detail[profile_url]:
            profiles_detail[profile_url]['blog_posts'] = {}
        profiles_detail[profile_url]['blog_posts'][blog_url] = partial_result(blog_url)

    for profile_url in profiles_detail:
        longest_blog = []     # the blog of the most words of the user
        max_words = -1        # number of words in longest_blog

        all_posts = []

        for blog_url in profiles_detail[profile_url]['blog_posts']:
            num_words = 0       # number of words in this blog
            for post in profiles_detail[profile_url]['blog_posts'][blog_url]:
                txt = post['content']
                soup = BeautifulSoup(txt)
                post['content'] = soup.get_text()               # parse the post in case of raw html format
                num_words += len(post['content'].split())

                all_posts.append(post)

            if num_words > max_words:
                max_words = num_words
                longest_blog = profiles_detail[profile_url]['blog_posts'][blog_url]

        if max_words < MIN_NUM_WORD:
            stmt = 'insert into invalid_profiles values(%s);'
            dbh1.exec_stmt(stmt, [profile_url])
            print 'This profile has too few words'
            continue
        
        ctx = {'blog_name': profiles_detail[profile_url]['name'].replace("\'", '')}
        #ctx['wf_vs_month'] = visualize.words_vs_time(posts=longest_blog, freq_words=[], group_by='month')
        #ctx['wf_vs_year'] = visualize.words_vs_time(posts=longest_blog, freq_words=[], group_by='year')
        #ctx['wf_vs_week'] = visualize.words_vs_time(posts=longest_blog, freq_words=[], group_by='week')
        #ctx['wf_vs_day'] = visualize.words_vs_time(posts=longest_blog, freq_words=[], group_by='day')
        ctx['word_cloud'] = visualize.word_cloud(longest_blog)

        token = get_token(profile_url)

        ctx['id'] = token
        ctx['surveys_taken'] = ', '.join(qualtrics_get.surveys_taken(profile_url)) 
        
        # compute the big_5 score before sending email
        visualize.get_personality(profile_url, all_posts, dbh1)

        send_email('renhzhang2@gmail.com', ctx) 
        
invite()
# send('renhzhang2@gmail.com')
