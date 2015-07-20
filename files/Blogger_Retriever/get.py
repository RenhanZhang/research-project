import requests
import urllib2
import ast
import nltk
from bs4 import BeautifulSoup
import re

api_key = 'AIzaSyAsO-ID5sIxbtvc59ir5v2xbVxZTA02VDo'


def parse_post(post):
    # extract year-month-day
    time_pat = '(\d{4})-(\d{2})-(\d{2})'
    (year, month, day) = re.search(time_pat, post['published']).groups()
    post['pub_year'] = year
    post['pub_month'] = month
    post['pub_day'] = day

    # use beautiful soup to parse the content
    soup = BeautifulSoup(post['content'])
    post['content'] = soup.get_text()

    # get author_id and the name
    post['author_id'] = post['author']['id']
    post['author_display_name'] = post['author']['displayName']

    return post

def get(url):
   # return the content in json format
    print url
    data = requests.get(url)
    return data.json()

def get_blog_by_link(blog_url):

    url = 'https://www.googleapis.com/blogger/v3/blogs/byurl?url=' + blog_url + '&key=' + api_key
    content = get(url)
    return get_blog_by_ID(content['id'])

def get_blog_by_ID(blog_id):

    get_all_posts_url = 'https://www.googleapis.com/blogger/v3/blogs/' + str(blog_id) + '/posts?key=' + api_key
    post_dict = get(get_all_posts_url)
    all_posts = []

    for post in post_dict['items']:
        post_id = post['id']
        get_post_url = 'https://www.googleapis.com/blogger/v3/blogs/%s/posts/%s?key=%s' %(str(blog_id), post_id, api_key)
        post_detail = get(get_post_url)

        all_posts.append(parse_post(post_detail))

    return all_posts

a = get_blog_by_link('http://googleblog.blogspot.com/')
b = 2
#get_blog_byID(2399953)