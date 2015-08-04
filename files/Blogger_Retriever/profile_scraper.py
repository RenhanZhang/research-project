from bs4 import BeautifulSoup as bs
import requests
import re
import MySQLdb
'''
This module is used to scrape the following attributes from a users' profile given his/her url
gender, industry, occupation, city, state, country, introduction,
interests, movies, music, books, name, image_url, email, web_page_url
instant_messaging_service  instant_messaging_username, blogs_following
'''

def scrape_profile(url):

    a = requests.get(url)
    s = bs(a.text, 'html.parser')
    profile = {}
    profile['url'] = url
    # if the connection is well established, we are sure to get an image_url
    # But when the request is blocked because of too frequent query to blogger.com,
    # there will be no image_url
    if not scrape_image_url(s, profile):
        a = 1

    scrape_blogs_followed(a.text, profile)
    scrape_email(s, profile)

    scrape_instant_message(s, profile)
    scrape_name(s, profile)
    scrape_web_page_url(s, profile)
    others(s, profile)

    for (k,v) in profile.items():
        if isinstance(v, basestring):
            profile[k] = re.sub(',$', '', v)
    return profile

def others(s, profile):
    # extract gender, industry, occupation, city, state, country, introduction,
    # interests, movies, music, books
    '''
    attrs = ['gender', 'industry', 'occupation', 'city', 'state', 'country', 'introduction',
             'interests', 'movies', 'music', 'books']
    '''
    synonyms = {'locality': 'city', 'region':'state', 'country-name': 'country'}
    for item in s.find_all('tr'):
        contents = item.contents
        category = contents[0].get_text()
        if category == 'Location':
            for entry in contents[2].find_all('span'):
                profile[synonyms[entry['class'][0]]] = entry.get_text()
        else:
            category = re.sub('favorite\s+', '', category.lower())
            profile[category.lower()] = '\n'.join([entry.get_text() for entry in contents[2:]])
    if 'gender' in profile:
        profile['gender'] = 1 if profile['gender'] == 'Male' else 0

    '''
    for attr in attrs:
        if attr not in profile:
            profile[attr] = None
    '''
def scrape_name(s, profile):

    title = s.title.get_text()
    profile['name'] = re.sub('Blogger: User Profile:', '', title).strip()

def scrape_image_url(s, profile):

    if not s.find(id='profile-photo'):
        return False
    profile['image_url'] = s.find(id='profile-photo')['src']
    return True

def scrape_email(s, profile):
    # email
    pattern = 'printEmail\("blog(.+)\.biz'
    email = None
    for item in s.find_all('li'):
        match = re.search(pattern, item.get_text())
        if match:
            email = match.group(1)

    profile['email'] = email

def scrape_web_page_url(s, profile):
    # web_page_url
    web_page_url = None
    for item in s.find_all(rel='me nofollow'):
        if item.get_text() == 'My Web Page':
            web_page_url = item['href']
    profile['web_page_url'] = web_page_url

def scrape_instant_message(s, profile):
    # instant_messaging_service  instant_messaging_username
    pattern = '<div class=\"\">(.+)</div>'
    instant_messaging_service, instant_messaging_username = None, None
    for item in s.find_all('li'):
        str = unicode(item)
        match = re.search(pattern, str)
        if match:
            instant_messaging_username = match.group(1)
            service_match = re.search('</div>\n\((.+)\)</li>', str)
            if service_match:
                instant_messaging_service = service_match.group(1)
            break
    profile['instant_messaging_service'] = instant_messaging_service
    profile['instant_messaging_username'] = instant_messaging_username

def scrape_blogs_followed(html, profile):
    # blogs_following
    blogs_following = []
    pat = '<h2>Blogs I follow</h2>(.+?)<div class="section-divider">'
    match = re.search(pat, html.replace('\n', ''))

    if match:
        soup = bs(match.group(1))
        for entry in soup.find_all('a'):
            blogs_following.append(entry['href'])

    profile['blogs_following'] = blogs_following











'''
p = scrape_profile('https://www.blogger.com/profile/00053106429388237359')
print sorted(p.keys())
print len(p.keys())

db = MySQLdb.connect(host="lit04.eecs.umich.edu", # your host, usually localhost
                     user="rhzhang", # your username
                      passwd="renhan", # your password
                      db="myblogs") # name of the data base



cur = db.cursor()

cur.execute('select * from profiles limit 100')
attrs = {'gender':1, 'industry':2, 'occupation':3, 'city':4, 'state':5, 'country':6,
        'introduction':7,'interests':8, 'movies':9, 'music':10, 'books':11, 'name':12, 'image_url':13,
        'email':14, 'web_page_url':15,'instant_messaging_service':16, 'instant_messaging_username':17}

for row in cur.fetchall():
    profile = scrape_profile(row[0])
    print '\n[[[[[[[[[[[[[[[[[[[[[[[[[%s]]]]]]]]]]]]]]]]]]]]]]]]]]]]' %row[0]

    for (k,v) in attrs.items():
        if isinstance(profile[k], basestring) and isinstance(row[v], basestring):
            if profile[k].replace('\s', '') == row[v].replace('\s', ''):
                continue
        if profile[k] != row[v]:
            print k
            print '=================================================================='
            print profile[k]
            print '----------------------------------------'
            print row[v]

'''