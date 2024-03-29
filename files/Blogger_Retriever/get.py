import requests, os
from bs4 import BeautifulSoup
import re
import profile_scraper
from dateutil import parser
import calendar
from DB_Handling import BlogsDB
import logging

dirname = os.path.dirname(os.path.abspath(__file__))

MAX_POSTS = 2500
MAX_TO_DISPLAY = 100

api_key = 'AIzaSyAsO-ID5sIxbtvc59ir5v2xbVxZTA02VDo'


def rm_special_char(s):
     
    special_char = [(u"\u2018", "'"), (u"\u2019", "'"), (u'\u201c', '"'),
                    (u'\u201d', '"'), (u"\u2014", '-'), (u'\u02bb', "'")]
    for u, v in special_char:
        s = s.replace(u, v)
    return s


def parse_time(s):

    d = parser.parse(s)
    return calendar.timegm(d.utctimetuple()) * 1000

def parse_post(post):
    # extract year-month-day
    '''
    time_pat = '(\d{4})-(\d{2})-(\d{2})'
    (year, month, day) = re.search(time_pat, post['published']).groups()
    post['pub_year'] = int(year)
    post['pub_month'] = int(month)
    post['pub_day'] = int(day)
    '''
    post['pub'] = post['published']
    post['published'] = parse_time(post['published'])
    post['updated'] = parse_time(post['updated'])
    # use beautiful soup to parse the content
    #ipdb.set_trace()
    soup = BeautifulSoup(post['content'].encode('ascii', 'ignore'))
    post['content'] = soup.get_text()

    return post

def get(url):
   # return the content in json format
    #ipdb.set_trace()
    print url
    data = requests.get(url)
    return data.json()

def get_blog_by_link(blog_url, latest, max_to_display=100):

    MAX_TO_DISPLAY = max_to_display
    #ipdb.set_trace()
    if not re.match('http', blog_url):
        blog_url = 'http://' + blog_url

    url = 'https://www.googleapis.com/blogger/v3/blogs/byurl?url=' + blog_url + '&key=' + api_key
    blog_summary = get(url)
   
    '''
    logging.basicConfig(filename=dirname + '/log.get',level=logging.DEBUG)
    logging.debug('url: %s\n blog_summary: %s\n' %(url, str(blog_summary)))
    assert 1==2
    '''

    if 'id' not in blog_summary:
        return None, None, None, None

    blog_summary['published'] = parse_time(blog_summary['published'])
    blog_summary['updated'] = parse_time(blog_summary['updated'])
    
    profile_url, posts, next_page_token = get_blog_by_ID(blog_summary['id'], latest)

    profile = None
    if profile_url:
        profile = profile_scraper.scrape_profile(profile_url)
    # ipdb.set_trace()
    return profile, blog_summary, posts, next_page_token

def get_blog_by_ID(blog_id, latest):

    get_blog_url = 'https://www.googleapis.com/blogger/v3/blogs/' + str(blog_id) + '/posts?key=' + api_key

    all_posts, hit_earliest, profile_url, next_page_token = [], False, None, None

    while not hit_earliest:

        blog_info = get(get_blog_url)

        if 'items' not in blog_info:
            break

        for post in blog_info['items']:

            post = parse_post(post)

            profile_url = post['author']['url']
            post['author_url'] = profile_url

            # if this is the latest post already in db
            if post['published'] <= latest:
                hit_earliest = True
                break
            all_posts.append(post)

        next_page_token = blog_info.get('nextPageToken', None)
        if not next_page_token:
            break
        else:
            get_blog_url = 'https://www.googleapis.com/blogger/v3/blogs/%s/posts?key=%s&pageToken=%s' \
                           %(str(blog_id), api_key, next_page_token)
            if len(all_posts) >= MAX_TO_DISPLAY:
                break
    if len(all_posts) > 0:
        all_posts = sorted(all_posts, key=lambda x: x['published'])
    return profile_url, all_posts, next_page_token

def get_remain_posts(blog_url, blog_id, init_pg_token, quota, earliest):

    url = 'https://www.googleapis.com/blogger/v3/blogs/%s/posts?key=%s&pageToken=%s' %(str(blog_id), api_key, init_pg_token)

    dbh = BlogsDB.BlogsDB_Handler()
    #ipdb.set_trace()
    while quota > 0:
        print 'parallel...'

        data = get(url)
        posts = [parse_post(post) for post in data['items']]
        quota -= len(posts)

        # update the database
        dbh.update_posts(posts)
        dbh.update_blog_posts(blog_url, posts)

        if posts[0]['published'] <= earliest:
            break

        next_page_token = data.get('nextPageToken', None)
        if next_page_token is None:
            break
        else:
            url = 'https://www.googleapis.com/blogger/v3/blogs/%s/posts?key=%s&pageToken=%s' \
                           %(str(blog_id), api_key, next_page_token)
    print 'parallel done'

    dbh.close()
