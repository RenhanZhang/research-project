import requests
from bs4 import BeautifulSoup
import re
import ipdb
import profile_scraper
MAX_POSTS = 100
api_key = 'AIzaSyAsO-ID5sIxbtvc59ir5v2xbVxZTA02VDo'


def rm_special_char(s):
     
    special_char = [(u"\u2018", "'"), (u"\u2019", "'"), (u'\u201c', '"'),
                    (u'\u201d', '"'), (u"\u2014", '-'), (u'\u02bb', "'")]
    for u, v in special_char:
        s = s.replace(u, v)
    return s

def parse_post(post):
    # extract year-month-day
    time_pat = '(\d{4})-(\d{2})-(\d{2})'
    (year, month, day) = re.search(time_pat, post['published']).groups()
    post['pub_year'] = int(year)
    post['pub_month'] = int(month)
    post['pub_day'] = int(day)
    # use beautiful soup to parse the content
    #ipdb.set_trace()
    soup = BeautifulSoup(post['content'])
    post['content'] = soup.get_text()

    return post

def get(url):
   # return the content in json format
    data = requests.get(url)
    return data.json()

def get_blog_by_link(blog_url):

    if not re.match('http', blog_url):
        blog_url = 'http://' + blog_url

    url = 'https://www.googleapis.com/blogger/v3/blogs/byurl?url=' + blog_url + '&key=' + api_key
    print url
    blog_summary = get(url)

    if 'id' not in blog_summary:
        return None, None
    posts = get_blog_by_ID(blog_summary['id'])

    if len(posts) > 0:
        profile_url = posts[0]['author']['url']

    profile = profile_scraper.scrape_profile(profile_url)
    return profile, blog_summary, posts

def get_blog_by_ID(blog_id):

    get_blog_url = 'https://www.googleapis.com/blogger/v3/blogs/' + str(blog_id) + '/posts?key=' + api_key

    all_posts = []

    while True:
        print get_blog_url
        blog_info = get(get_blog_url)

        for post in blog_info['items']:
            post_id = post['id']
            get_post_url = 'https://www.googleapis.com/blogger/v3/blogs/%s/posts/%s?key=%s' %(str(blog_id), post_id, api_key)
            print get_post_url
            post_detail = get(get_post_url)
            all_posts.append(parse_post(post_detail))

        if len(all_posts) >= MAX_POSTS:
            break

        # ipdb.set_trace()
        # if all the posts have been obtained
        next_page_token = blog_info.get('nextPageToken', None)
        if next_page_token is None:
            break
        else:
            get_blog_url = 'https://www.googleapis.com/blogger/v3/blogs/%s/posts?key=%s&pageToken=%s' \
                           %(str(blog_id), api_key, next_page_token)

    return all_posts

#a = get_blog_by_link('http://d2r-travel.blogspot.com/')
#get_blog_byID(2399953)
