import MySQLdb
from dateutil import parser
import calendar
import ipdb
debug = True
import os
class BlogsDB_Handler:

    def __init__(self):
        info = self.read_db_setting()
        self.conn = MySQLdb.connect(host = info['host'],
                                  user = info['user'],
                                  passwd = info['passwd'],
                                  db = info['db_name'])
        # ipdb.set_trace()
        self.cur = self.conn.cursor()

    def read_db_setting(self):
        '''
         read host, user, passwd, db name from db_account.txt
         In the db_account.txt file, the format is [attribute]=[value].
         for example: host=localhost
        '''
        account_info = {}
        with open('DB_Handling/db_account.txt', 'r') as f:
            l = f.readlines()
            for str in l:
                (attr, val) = str.split('=')
                account_info[attr] = val.replace('\n', '')
        return account_info

    def batch_update(self, profile, blog, posts):
        print '\n\n-------------------blogs--------------------'
        self.update_blog(blog)
        print '\n\n-------------------posts--------------------'
        self.update_posts(posts)
        print '\n\n-------------------blogs_posts--------------------'
        self.update_blog_posts(blog, posts)

        if profile:
            print '\n\n-------------------profiles--------------------'
            self.update_profile(profile)
            print '\n\n-------------------profiles_blog--------------------'
            self.update_profile_blogs(profile, blog)
            print '\n\n-------------------profiles_blogs_followed--------------------'
            self.update_profile_blogs_followed(profile)

    def update_blog(self, blog):
        self.prepare_blog(blog)
        stmt = 'insert into blogs values (%s, %s, %s, %s, %s, %s, %s, %s) on duplicate key update;' \
               %(blog['url'], blog['description'], blog['name'], blog['published'],\
                 blog['updated'], blog['locale']['country'], blog['locale']['language'],\
                 blog['locale']['variant'])
        if debug:
            print stmt
        else:
            self.exec_stmt(stmt)

    def prepare_blog(self, blog):
        attrs = ['url', 'description', 'name']
        '''
        for attr in attrs:
            if attr not in blog or not blog[attr] or blog[attr] == '':
                blog[attr] = 'NULL'
            else: blog[attr] = '\'' + blog[attr] + '\''
        '''
        self.prepare_str(blog, attrs)
        self.parse_time(blog, 'published')
        self.parse_time(blog, 'updated')

        if 'locale' not in blog:
            blog['locale'] = {}
        self.prepare_str(blog['locale'], ['language', 'country', 'variant'])

    def update_posts(self, posts):
        for post in posts:
            self.prepare_post(post)
            stmt = 'insert into posts values(%s, %s, %s, %s, %s, %s, %s, %s, %s) on duplicate key update;' \
                   %(post['url'], post['title'], post['content'], post['published'], post['author_url'],\
                     post['location']['lat'], post['location']['lng'], post['location']['name'], post['location']['span'])
            if debug:
                print stmt
            else:
                self.exec_stmt(stmt)

    def prepare_post(self, post):
        if 'author' in post:
            post['author_url'] = post['author'].get('url', None)
        else:
            post['author_url'] = None

        self.parse_time(post, 'published')
        attr = ['url', 'title', 'content', 'author_url']
        # ipdb.set_trace()
        self.prepare_str(post, attr)

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
        self.prepare_str(post['location'], ['name', 'lat', 'lng', 'span'])

    def update_profile(self, p):
        self.prepare_profile(p)
        if self.cur.execute('select * from blogs where url=%s' %p['url']):
            return
        # ipdb.set_trace()
        stmt = 'insert into profiles values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) on duplicate key update;'\
                %(p['url'], p['gender'], p['industry'], p['occupation'], p['city'],\
                  p['state'], p['country'], p['introduction'], p['interests'], p['movies'],\
                  p['music'], p['books'], p['name'], p['image_url'], p['email'], p['web_page_url'],\
                  p['instant_messaging_service'], p['instant_messaging_username'])
        if debug:
            print stmt
        else:
            self.exec_stmt(stmt)



    def prepare_profile(self, profile):

        # prepare profile into a format suitable for database
        attrs = ['url', 'interests','city','name','instant_messaging_username',
                 'introduction','gender','industry','instant_messaging_service',
                 'movies','state','books','music','country','image_url','email',
                 'web_page_url','occupation']
        self.prepare_str(profile, attrs)


    def update_blog_posts(self, blog, posts):
        for post in posts:
            stmt = 'insert into blogs_posts values (%s, %s) on duplicate key update;' %(blog['url'], post['url'])
            if debug:
                print stmt
            else:
                self.exec_stmt(stmt)

    def update_profile_blogs(self, profile, blog):

        stmt = 'insert into profiles_blogs values (%s, %s) on duplicate key update;' %(profile['url'], blog['url'])
        if debug:
            print stmt
        else:
            self.exec_stmt(stmt)

    def update_profile_blogs_followed(self, profile):
        for blog_url in profile['blogs_following']:
            stmt = 'insert into profiles_blogs_followed values (%s, %s) on duplicate update;' %(profile['url'], '\''+blog_url+'\'')
            if debug:
                print stmt
            else:
                self.exec_stmt(stmt)


    def prepare_str(self, dictionary, attrs):
        for attr in attrs:
            if attr not in dictionary or not dictionary[attr]:
                dictionary[attr] = 'NULL'
            elif isinstance(dictionary[attr], basestring):
                #if dictionary[attr] == '':
                #    dictionary[attr] = 'NULL'
                #else: dictionary[attr] = '\'' + dictionary[attr] + '\''
                dictionary[attr] = '\'' + dictionary[attr] + '\''

    def parse_time(self, dictionary, attr):
        if attr in dictionary:
            d = parser.parse(dictionary[attr])
            dictionary[attr] = str(calendar.timegm(d.utctimetuple()) * 1000)
        else:
            dictionary[attr] = 'NULL'

    def exec_stmt(self, stmt):
        try:
            self.cur.execute(stmt)

        except MySQLdb.Error as e:
            try:
                print "MySQL Error [%d]: %s" % (e.args[0], e.args[1])
            except IndexError:
                print "MySQL Error: %s" % str(e)
