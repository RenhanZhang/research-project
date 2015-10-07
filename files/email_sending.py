import re, os, smtplib, datetime, string, random, datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from search_blogs import search_views
from bs4 import BeautifulSoup 
from TextVisualize import visualize
from DB_Handling import BlogsDB

with open('email_account.txt', 'r') as f:
    username = f.readline().split()[1]
    pwd = f.readline().split()[1]

MIN_NUM_WORD = 1000
dirname = os.path.dirname(os.path.abspath(__file__))

def send_email(recepient, contents={}):
    
    # Create message container - the correct MIME type is multipart/alternative.
    msg = MIMEMultipart('alternative')
    msg['Subject'] = "Testing"
    msg['From'] = me
    msg['To'] = recepient

    # load the html body
    with open(dirname + '/email_embedded.html', 'r') as f:
        html = f.read()

    html = html.format(blog_name=contents['blog_name'],
                       wf_vs_month=contents['wf_vs_month'],
                       wf_vs_year=contents['wf_vs_year'],
                       wf_vs_week=contents['wf_vs_week'],
                       wf_vs_day=contents['wf_vs_day'])
    html = re.sub('{word_cloud}', contents['word_cloud'], html)

    '''
    with open(str(datetime.datetime.now())+'.html', 'w') as f:
        f.write(html)
    '''
    
    # Record the MIME types of both parts - text/plain and text/html.
    # part1 = MIMEText(text, 'plain')
    part2 = MIMEText(html, 'html')

    msg.attach(part2)

    # Send the message via local SMTP server.
    server = smtplib.SMTP('smtp.gmail.com:587')
    server.ehlo()
    server.starttls()
    server.login(username,pwd)
    server.sendmail(username, recepient, msg.as_string())
    server.quit()
    
def id_gen(length=8):
    dbh = BlogsDB.BlogsDB_Handler()

    while True:
        token = ''.join(random.choice(chars) for _ in range(length))

        cmd = '''
                  select profile_url 
                  from profiles_surveys 
                  where code = %s;
              '''
        if len(dbh.exec_and_get(cmd, [token])) == 0:
            return token

def invite():
    dbh1 = BlogsDB.BlogsDB_Handler()  # used to get all the valid profiles and necessary info
    cmd = '''
          select p.url, p.email, posts.content, blogs_posts.blog_url from 
          (select url, email from profiles 
           where profiles.url not in (select profile_url from profiles_surveys) and email is not null
          ) as p, profiles_blogs, blogs_posts, posts 
          where p.url = profiles_blogs.profile_url and profiles_blogs.blog_url = blogs_posts.blog_url and blogs_posts.post_url = posts.url;
          '''
    cmd = '''
          select p.url, p.email, blogs_posts.blog_url from 
          (select url, email from profiles 
           where profiles.url not in (select profile_url from profiles_surveys) and email is not null
          ) as p, profiles_blogs, blogs_posts 
          where p.url = profiles_blogs.profile_url and p.email is not null;
          '''
    cmd = '''
          select p.url, p.email, pb.blog_url, blogs.name 
          from profiles as p, profiles_blogs as pb, blogs 
          where p.url = pb.profile_url 
          and pb.blog_url = blogs.url
          and p.email is not null
          and p.url not in (select url from invalid_profiles) 
          and p.url not in (select profile_url from profiles_surveys)
          limit 10;
          '''

    profiles_detail = {} 

    for e in dbh1.exec_and_get(stmt=cmd):
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
        profiles_detail[profile_url]['blog_posts'][blog_url] = search_views.partial_result(blog_url)


    for profile_url in profiles_detail:
        longest_blog = []     # the blog of the most words of the user
        max_words = -1        # number of words in longest_blog
        for blog_url in profiles_detail[profile_url]['blog_posts']:
            num_words = 0       # number of words in this blog
            for post in profiles_detail[profile_url]['blog_posts'][blog_url]:
                txt = post['content']
                soup = BeautifulSoup(txt)
                post['content'] = soup.get_text()               # parse the post in case of raw html format
                num_words += len(post['content'].split())
            if num_words > max_words:
                max_words = num_words
                longest_blog = profiles_detail[profile_url]['blog_posts'][blog_url]

        if max_words < MIN_NUM_WORD:
            stmt = 'insert into invalid_profiles values(%s);'
            dbh1.exec_stmt(stmt, [profile_url])
            print 'This profile has too few words'
            continue
        
        ctx = {'blog_name': profiles_detail[profile_url]['name'].replace("\'", '')}

        # visualization
        ctx['wf_vs_month'] = visualize.words_vs_time(posts=longest_blog, freq_words=[], group_by='month')
        ctx['wf_vs_year'] = visualize.words_vs_time(posts=longest_blog, freq_words=[], group_by='year')
        ctx['wf_vs_week'] = visualize.words_vs_time(posts=longest_blog, freq_words=[], group_by='week')
        ctx['wf_vs_day'] = visualize.words_vs_time(posts=longest_blog, freq_words=[], group_by='day')
        ctx['word_cloud'] = visualize.word_cloud(longest_blog)

        send_email('renhzhang2@gmail.com', ctx)
        token = id_gen()
        ctx['id'] = token
        stmt = 'insert into profiles_surveys(profile_url, code) values(%s, %s);'
        dbh1.exec_stmt(stmt, [profile_url, token])
    
invite()
# send('renhzhang2@gmail.com')