import MySQLdb
from dateutil import parser
import calendar
import ipdb
import os
import time
from copy import deepcopy

DEBUG = False
EXEC = True

BLOG_ATTR = ['url', 'description', 'name', 'published', 'updated', 'locale']
POST_ATTR = ['url', 'title', 'content', 'published', 'author_url', 'location']
class BlogsDB_Handler:

    def __init__(self):
        info = self.read_db_setting()
        '''
        self.conn = MySQLdb.connect(host = info['host'],
                                  user = info['user'],
                                  passwd = info['passwd'],
                                  db = info['db_name'],
                                  charset='utf8')
        '''
        self.conn = MySQLdb.connect(host='lit04.eecs.umich.edu',
                                    user='rhzhang',
                                    passwd='johnjohn',
                                    db='myblogs',
                                    charset='utf8')
        # ipdb.set_trace()
        self.cur = self.conn.cursor()

    def close(self):
        self.cur.close()
        self.conn.close()

    def read_db_setting(self):
        '''
         read host, user, passwd, db name from db_account.txt
         In the db_account.txt file, the format is [attribute]=[value].
         for example: host=localhost
        '''
        account_info = {}
        with open(os.path.dirname(os.path.abspath(__file__))+'/db_account.txt', 'r') as f:
            l = f.readlines()
            for str in l:
                (attr, val) = str.split('=')
                account_info[attr] = val.replace('\n', '')
        return account_info

    def batch_update(self, profile, blog, posts):
        #ipdb.set_trace()
        print '\n\n-------------------blogs--------------------'
        self.update_blog(blog)
        print '\n\n-------------------posts--------------------'
        self.update_posts(posts)
        print '\n\n-------------------blogs_posts--------------------'
        self.update_blog_posts(blog['url'], posts)

        if 'image_url' in profile:
            print '\n\n-------------------profiles--------------------'
            self.update_profile(profile)
            print '\n\n-------------------profiles_blog--------------------'
            self.update_profile_blogs(profile, blog)
            print '\n\n-------------------profiles_blogs_followed--------------------'
            self.update_profile_blogs_followed(profile)
        #self.conn.commit()

    def get_posts_in_blog(self, url):
        stmt = u"select url, title, content, published, author_url, " \
               u"location_latitude, location_longitude, location_name, location_span from blogs_posts as bp, posts as p \
                 where bp.blog_url = %s and bp.post_url = p.url order by published;"

        self.exec_stmt(stmt, [url])

        attrs = {'url':0, 'title':1, 'content':2, 'published':3, 'author_url':4, \
                'location_latitude':5, 'location_longitude':6, 'location_name':7, 'location_span':8}
        posts = []
        for tpl in self.cur.fetchall():
            post = {}
            for attr in attrs:
                post[attr] = tpl[attrs[attr]]
            posts.append(post)

        #posts = sorted(posts, key=lambda x: x['published'], reverse=True)

        # ensure all posts are in descending chronical order
        assert all(posts[i]['published'] <= posts[i+1]['published'] for i in xrange(len(posts)-1))
        return posts


    def update_blog(self, blog):
        blog = deepcopy(blog)
        self.prepare_blog(blog)
        stmt = u'insert into blogs\
                 values (%s, %s, %s, %s, %s, %s, %s, %s)\
                 on duplicate key\
                 update url = %s, description = %s, name = %s, published = %s,\
                 updated = %s, locale_country = %s, locale_language = %s, locale_variant = %s;'

        params = [blog['url'], blog['description'], blog['name'], blog['published'],blog['updated'],
                  blog['locale']['country'], blog['locale']['language'], blog['locale']['variant']]

        params.extend(params)
        #ipdb.set_trace()

        self.exec_stmt(stmt, params)

    def prepare_blog(self, blog):

        self.prepare_attr(blog, [x for x in BLOG_ATTR if x != 'locale'])

        if 'locale' not in blog:
            blog['locale'] = {}

        self.prepare_attr(blog['locale'], ['country', 'language', 'variant'])

    def update_posts(self, posts):
        posts = deepcopy(posts)
        for post in posts:
            self.prepare_post(post)
            stmt = u'insert into posts values(%s, %s, %s, %s, %s, %s, %s, %s, %s)\
                    on duplicate key\
                    update url = %s, title = %s, content = %s, published = %s, author_url = %s,\
                    location_latitude = %s, location_longitude = %s, location_name = %s, location_span = %s;'

            params = [post['url'], post['title'], post['content'], post['published'], post['author_url'],
                      post['location']['lat'], post['location']['lng'], post['location']['name'], post['location']['span']]
            params.extend(params)

            self.exec_stmt(stmt, params)

    def prepare_post(self, post):
        if 'author' in post:
            post['author_url'] = post['author'].get('url', None)
        else:
            post['author_url'] = None

        attrs = ['url', 'title', 'content', 'published']
        self.prepare_attr(post, attrs)
        #ipdb.set_trace()

        # prepare for location info
        ''' "location": {
                "name": "Bundalong VIC 3730, Australia",
                "lat": -36.0300559,
                "lng": 146.16002660000004,
                "span": "0.205405,0.322723"
             }
        '''
        if 'location' not in post:
            post['location'] = {}
        self.prepare_attr(post['location'], ['name', 'lat', 'lng', 'span'])

    def update_profile(self, p):
        p = deepcopy(p)
        # ipdb.set_trace()

        stmt = u'insert into profiles values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)\
                 on duplicate key update\
                 url=%s, gender=%s, industry=%s, occupation=%s, city=%s, state=%s, country=%s, \
                introduction=%s, interests=%s, movies=%s, music=%s, books=%s, name=%s, \
                image_url=%s, email=%s, web_page_url=%s, instant_messaging_service=%s, instant_messaging_username=%s;'

        attrs = ['url', 'gender', 'industry', 'occupation', 'city',
                 'state', 'country', 'introduction', 'interests', 'movies',
                 'music', 'books', 'name', 'image_url', 'email', 'web_page_url',
                 'instant_messaging_service', 'instant_messaging_username']
        self.prepare_attr(p, attrs)
        params = [p[x] for x in attrs]

        params.extend(params)
        self.exec_stmt(stmt, params)

    def update_blog_posts(self, blog_url, posts):

        for post in posts:
            stmt = u"insert ignore into blogs_posts values (%s, %s);"
            params = (blog_url, post['url'])

            self.exec_stmt(stmt, params)

    def update_profile_blogs(self, profile, blog):

        stmt = u"insert ignore into profiles_blogs values (%s, %s);"
        params = [profile['url'], blog['url']]

        self.exec_stmt(stmt, params)

    def update_profile_blogs_followed(self, profile):
        for blog_url in profile['blogs_following']:
            stmt = u"insert ignore into profiles_blogs_followed values (%s, %s);"
            params = [profile['url'], blog_url]
            # ipdb.set_trace()

            self.exec_stmt(stmt, params)


    def prepare_attr(self, dictionary, attrs):
        # escape_pairs = {'\\': '\\\\', '"': '\\"', '\'': '\\\'', '%': '\\%', '\n': '\\n', '\t': '\\t', '_': '\\_'}
        for attr in attrs:
            if attr not in dictionary:
                dictionary[attr] = None

    def parse_time(self, dictionary, attr):
        if attr in dictionary:
            d = parser.parse(dictionary[attr])
            dictionary[attr] = str(calendar.timegm(d.utctimetuple()) * 1000)
        else:
            dictionary[attr] = 'NULL'

    def exec_stmt(self, stmt, params):
        #time.sleep(0.1)
        
        try:
            self.cur.execute(stmt, params)
            if len(self.cur.messages) > 0:
                print '----------------------Error--------------------'
                print stmt
                print '-------------------\n%s' %self.cur.messages
            self.conn.commit()

        except MySQLdb.Error as e:
            print stmt

            try:
                print "MySQL Error [%d]: %s" % (e.args[0], e.args[1])
            except IndexError:
                print "MySQL Error: %s" % str(e)
