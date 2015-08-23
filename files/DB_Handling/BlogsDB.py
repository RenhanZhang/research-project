import MySQLdb
from dateutil import parser
import calendar
import ipdb
import os
import time
from copy import deepcopy

DEBUG = False
EXEC = True

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
        print '\n\n-------------------blogs--------------------'
        self.update_blog(blog)
        print '\n\n-------------------posts--------------------'
        self.update_posts(posts)
        print '\n\n-------------------blogs_posts--------------------'
        self.update_blog_posts(blog['url'], posts)

        if profile:
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
                 where bp.blog_url = '%s' and bp.post_url = p.url order by published;" %url

        self.exec_stmt(stmt)

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
                 values ({url}, {desc}, {name}, {pub}, {updt}, {loc_c}, {loc_lang}, {loc_var})\
                 on duplicate key\
                 update url = {url}, description = {desc}, name = {name}, published = {pub},\
                 updated = {updt}, locale_country = {loc_c}, locale_language = {loc_lang}, locale_variant = {loc_var};'\
                 .format(url = blog['url'], desc = blog['description'], name = blog['name'], pub = blog['published'],\
                 updt = blog['updated'], loc_c = blog['locale']['country'], loc_lang = blog['locale']['language'],\
                 loc_var = blog['locale']['variant'])


        '''
        stmt = u'insert into blogs values (%s, %s, %s, %s, %s, %s, %s, %s) on duplicate key update;' \
               %(blog['url'], blog['description'], blog['name'], blog['published'],\
                 blog['updated'], blog['locale']['country'], blog['locale']['language'],\
                 blog['locale']['variant'])
        '''
        #ipdb.set_trace()

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
        #self.parse_time(blog, 'published')
        #self.parse_time(blog, 'updated')

        if 'locale' not in blog:
            blog['locale'] = {}
        self.prepare_str(blog['locale'], ['language', 'country', 'variant'])

    def update_posts(self, posts):
        posts = deepcopy(posts)
        for post in posts:
            self.prepare_post(post)
            stmt = u'insert into posts values({url}, {title}, {cont}, {pub}, {auth_url}, {loc_lat}, {loc_lng}, {loc_name}, {loc_span})\
                    on duplicate key\
                    update url = {url}, title = {title}, content = {cont}, published = {pub}, author_url = {auth_url},\
                    location_latitude = {loc_lat}, location_longitude = {loc_lng}, location_name = {loc_name}, location_span = {loc_span};'\
            .format(url=post['url'], title=post['title'], cont=post['content'], pub=post['published'], auth_url=post['author_url'],\
                     loc_lat=post['location']['lat'], loc_lng=post['location']['lng'], loc_name=post['location']['name'],
                    loc_span=post['location']['span'])

            self.exec_stmt(stmt)

    def prepare_post(self, post):
        if 'author' in post:
            post['author_url'] = post['author'].get('url', None)
        else:
            post['author_url'] = None

        #self.parse_time(post, 'published')
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
        p = deepcopy(p)
        self.prepare_profile(p)
        if self.cur.execute('select * from blogs where url=%s' %p['url']):
            return
        # ipdb.set_trace()

        stmt = u'insert into profiles values({url}, {gend}, {indst}, {occu}, {city}, {state}, {country}, {intro}, \
                {ints}, {movie}, {music}, {books}, {name}, {img_url}, {email}, {web_url}, {sms}, {sms_name} \
                on duplicate key update url={url}, gender={gend}, industry={indst}, occupation{occu}, city={city}, state={state}, country={country}, \
                introduction={intro}, interests={ints}, movies={movie}, music={music}, books={books}, name={name}, \
                image_url={img_url}, email={email}, web_page_url={web_url}, instant_messaging_service={sms}, instant_messaging_username={sms_name};'\
                .format(url=p['url'], gend=p['gender'], indst=p['industry'], occu=p['occupation'], city=p['city'],\
                  state=p['state'], country=p['country'], intro=p['introduction'], ints=p['interests'], movie=p['movies'],\
                  music=p['music'], books=p['books'], name=p['name'], img_url=p['image_url'], email=p['email'], web_url=p['web_page_url'],\
                  sms=p['instant_messaging_service'], sms_name=p['instant_messaging_username'])
        self.exec_stmt(stmt)

    def prepare_profile(self, profile):

        # prepare profile into a format suitable for database
        attrs = ['url', 'interests','city','name','instant_messaging_username',
                 'introduction','gender','industry','instant_messaging_service',
                 'movies','state','books','music','country','image_url','email',
                 'web_page_url','occupation']
        self.prepare_str(profile, attrs)


    def update_blog_posts(self, blog_url, posts):

        for post in posts:
            stmt = u"insert ignore into blogs_posts values ('%s', '%s');" %(blog_url, post['url'])

            self.exec_stmt(stmt)

    def update_profile_blogs(self, profile, blog):

        stmt = u"insert ignore into profiles_blogs values ('%s', '%s');" %(profile['url'], blog['url'])

        self.exec_stmt(stmt)

    def update_profile_blogs_followed(self, profile):
        for blog_url in profile['blogs_following']:
            stmt = u"insert into ignore profiles_blogs_followed values ('%s', '%s');" %(profile['url'], blog_url)

            self.exec_stmt(stmt)


    def prepare_str(self, dictionary, attrs):
        escape_pairs = {'\\': '\\\\', '"': '\\"', '\'': '\\\'', '%': '\\%', '\n': '\\n', '\t': '\\t', '_': '\\_'}
        for attr in attrs:
            if attr not in dictionary or not dictionary[attr]:
                dictionary[attr] = 'NULL'
            elif isinstance(dictionary[attr], basestring):
                #if dictionary[attr] == '':
                #    dictionary[attr] = 'NULL'
                #else: dictionary[attr] = '\'' + dictionary[attr] + '\''
                for pat in escape_pairs:
                    dictionary[attr] = dictionary[attr].replace(pat, escape_pairs[pat])

                dictionary[attr] = '\'' + '\''

    def parse_time(self, dictionary, attr):
        if attr in dictionary:
            d = parser.parse(dictionary[attr])
            dictionary[attr] = str(calendar.timegm(d.utctimetuple()) * 1000)
        else:
            dictionary[attr] = 'NULL'

    def exec_stmt(self, stmt):
        #time.sleep(0.1)
        try:
            self.cur.execute(stmt)
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
