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

cmd = 'select pf.url as profile_url, po.content \
       from profiles as pf, profiles_blogs as p_b, blogs_posts as b_p, posts as po \
       where \
       pf.url = p_b.profile_url and p_b.blog_url = b_p.blog_url and b_p.post_url = po.url limit 500000;'

cur.execute(cmd)

dic = {}
count = 0
for e in cur:
    count += 1
    raw_text = e[1].encode('utf-8')
    soup = BeautifulSoup(raw_text)
    text = soup.get_text()
    #print '--------------------------------------------------'
    #print text
    dic[e[0]] = dic.get(e[0], 0) + len(text.split())
    del e
    print count


with open('result_partial.csv', 'a') as f:
    for p in dic:
        f.write(p + ', ' + str(dic[p]) + '\n')