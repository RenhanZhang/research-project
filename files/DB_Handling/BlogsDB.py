import MySQLdb
from dateutil import parser
import time
import ipdb
debug = True
class BlogsDB_Handler:

    def __init__(self):
        self.db = MySQLdb.connect(host='lit04.eecs.umich.edu',
                                  user = 'rhzhang',
                                  passwd = 'renhan',
                                  db = 'myblogs')
        self.cur = self.db.cursor()

    def batch_update(self, profile, blog, posts):
        print '\n\n-------------------blogs--------------------'
        self.update_blog(blog)
        print '\n\n-------------------posts--------------------'
        self.update_posts(posts)
        print '\n\n-------------------profiles--------------------'
        self.update_profile(profile)
        print '\n\n-------------------blogs_posts--------------------'
        self.update_blog_posts(blog, posts)
        print '\n\n-------------------profiles_blog--------------------'
        self.update_profile_blogs(profile, blog)
        print '\n\n-------------------profiles_blogs_followed--------------------'
        self.update_profile_blogs_followed(profile)

    def update_profile(self, p):
        self.prepare_profile(p)
        if self.cur.execute('select * from blogs where url=%s' %p['url']):
            return
        ipdb.set_trace()
        stmt = 'insert into profiles values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'\
                %(p['url'], p['gender'], p['industry'], p['occupation'], p['city'],\
                  p['state'], p['country'], p['introduction'], p['interests'], p['movies'],\
                  p['music'], p['books'], p['name'], p['image_url'], p['email'], p['web_page_url'],\
                  p['instant_messaging_service'], p['instant_messaging_username'])
        if debug:
            print stmt
        else:
            self.cur.execute(stmt)

    def prepare_profile(self, profile):

        # prepare profile into a format suitable for database
        attrs = ['url', 'interests','city','name','instant_messaging_username',
                 'introduction','gender','industry','instant_messaging_service',
                 'movies','state','books','music','country','image_url','email',
                 'web_page_url','occupation']
        self.prepare_str(profile, attrs)

        '''
        for attr in attrs:
            if attr not in profile or not profile[attr]:
                profile[attr] = 'NULL'
            elif isinstance(profile[attr], basestring):
                if profile[attr] == '':
                    profile[attr] = 'NULL'
                else: profile[attr] = '\'' + profile[attr] + '\''
        '''

    '''
    def update_blogs_followed(self, profile):
        for blog in profile['scrape_blogs_following']:
            stmt = 'insert into profiles_blogs_followed values (%s, %s)'\
                             % (profile['url'], '\'' + blog + '\''))
            if debug:
                print stmt
            else:
                self.cur.execute(stmt)
    '''
    def update_blog(self, blog):
        self.prepare_blog(blog)
        stmt = 'insert into blogs values (%s, %s, %s, %s, %s, %s, %s, %s)' \
               %(blog['url'], blog['description'], blog['name'], blog['published'],\
                 blog['updated'], blog['locale']['country'], blog['locale']['language'],\
                 blog['locale']['variant'])
        if debug:
            print stmt
        else:
            self.cur.execute(stmt)

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
            stmt = """insert into posts (url, title, content, published, author_url)
                      values(%s, %s, %s, %s, %s)""" \
                   %(post['url'], post['title'], post['content'], post['published'], post['author_url'])
            if debug:
                print stmt
            else:
                self.cur.execute(stmt)

    def prepare_post(self, post):
        if 'author' in post:
            post['author_url'] = post['author'].get('url', None)
        else:
            post['author_url'] = None

        self.parse_time(post, 'published')
        attr = ['url', 'title', 'content', 'author_url']
        self.prepare_str(post, attr)

    def update_blog_posts(self, blog, posts):
        for post in posts:
            stmt = 'insert into blogs_posts values (%s, %s)' %(blog['url'], post['url'])
            if debug:
                print stmt
            else:
                self.cur.execute(stmt)

    def update_profile_blogs(self, profile, blog):

        stmt = 'insert into profiles_blogs values (%s, %s)' %(profile['url'], blog['url'])
        if debug:
            print stmt
        else:
            self.cur.execute(stmt)

    def update_profile_blogs_followed(self, profile):
        for blog in profile['blogs_following']:
            stmt = 'insert into profiles_blogs_followed values (%s, %s)' %(profile['url'], '\''+blog+'\'')
            if debug:
                print stmt
            else:
                self.cur.execute(stmt)

    def update_blog_posts(self, blog, posts):
        for post in posts:
            stmt = 'insert into blogs_posts values (%s, %s)' %(blog['url'], post['url'])
            if debug:
                print stmt
            else:
                self.cur.execute(stmt)



    def prepare_str(self, dictionary, attrs):
        for attr in attrs:
            if attr not in dictionary or not dictionary[attr]:
                dictionary[attr] = 'NULL'
            elif isinstance(dictionary[attr], basestring):
                if dictionary[attr] == '':
                    dictionary[attr] = 'NULL'
                else: dictionary[attr] = '\'' + dictionary[attr] + '\''

    def parse_time(self, dictionary, attr):
        if attr in dictionary:
            d = parser.parse(dictionary[attr])
            dictionary[attr] = str(time.mktime(d.utctimetuple()) * 1000)
        else:
            dictionary[attr] = 'NULL'