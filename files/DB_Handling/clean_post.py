import MySQLdb
import MySQLdb.cursors
from bs4 import BeautifulSoup
import gc
conn = MySQLdb.connect(host='lit04.eecs.umich.edu',
                       user='rhzhang',
                       passwd='johnjohn',
                       db='myblogs',
                       charset='utf8',
                       cursorclass = MySQLdb.cursors.SSCursor)

# ipdb.set_trace()
cur = conn.cursor()

def clean():

  cmd = '''
            select url, content from posts 
            where url not in (select post_url from cleaned_posts)
            limit 50000;
        '''
  # cmd = u"select url from posts limit 500;"
  cur.execute(cmd)

  if cur.rowcount < 1:
      return False

  dic = {}

  for e in cur:
      raw_text = e[1].encode('utf-8')
      soup = BeautifulSoup(raw_text)
      text = soup.get_text()
      #print '--------------------------------------------------'
      #print text
      dic[e[0]] = text
      del e
  
  for post_url in dic:
      update_cmd = u"update posts set content = '%s' where url = '%s';" %(dic[post_url], post_url)
      cur.execute(cmd)

      record_cmd = u"insert into cleaned_posts values('%s')" % post_url

  return True

while True:
    if not clean():
        break

