from bs4 import BeautifulSoup as bs
import requests
import re
'''
This module is used to scrape the following attributes from a users' profile given his/her url
url, gender, industry, occupation, city, state, country, introduction,
interests, movies, music, books, name, image_url, email, web_page_url
instant_messaging_service  instant_messaging_username, blogs_following
'''

def scrape_profile(url):

    a = requests.get(url)
    s = bs(a.text)
    profile = {}


def others(s, profile):
    # extract gender, industry, occupation, city, state, country, introduction,
    # interests, movies, music, books
    synonyms = {'locality': 'city', 'region':'state', 'country-name': 'country'}
    for item in s.find_all('tr'):
        contents = item.contents
        category = contents[0].get_text()
        if category == 'Location':
            for entry in contents[2].find_all('span'):
                profile[synonyms[entry['class'][0]]] = entry.get_text()

        else:
            profile[category] = ', '.join([entry.get_text() for entry in contents[2:]])

def scrape_
# name
title = s.title.get_text()
profile['name'] = re.sub('Blogger: User Profile:', '', title).strip()

# image_url
profile['image_url'] = s.find(id='profile-photo')['src']

# email
pattern = 'printEmail\("blog(.+)\.biz'
email = None
for item in s.find_all('li'):
    match = re.search(pattern, item.get_text())
    if match:
        email = match.group(1)

profile['email'] = email

# web_page_url
web_page_url = None
for item in s.find_all(rel='me nofollow'):
    if item.get_text() == 'My Web Page':
        web_page_url = item['href']
profile['web_page_url'] = web_page_url

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

# blogs_following
blogs_following = []
pat = '<h2>Blogs I follow</h2>(.+?)<div class="section-divider">'
match = re.search(pat, a.text.replace('\n', ''))

if match:
    soup = bs(match.group(1))
    for entry in soup.find_all('a'):
        blogs_following.append(entry['href'])
profile['blogs_following'] = blogs_following

'''
print profile['instant_messaging_service']
print profile['instant_messaging_username']
print profile['email']
'''
print profile
for (k,v) in profile.items():
    if isinstance(v, basestring):
        profile[k] = re.sub(',$', '', v)