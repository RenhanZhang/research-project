import MySQLdb
class BlogsDB_Handler:

    def __init__():
        self.db = MySQLdb.connect(host='lit04.eecs.umich.edu',
                                  user = 'rhzhang',
                                  passwd = 'renhan',
                                  db = 'myblogs')

    def insert_blog(blog):
        
        ''' blog: a dictionary-like object contains info
                  as in the
        '''

        a = 1
