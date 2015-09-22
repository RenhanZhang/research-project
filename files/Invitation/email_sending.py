import smtplib
import re
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
from DB_Handling import BlogsDB

me = "litumich@gmail.com"

dirname = os.path.dirname(os.path.abspath(__file__))

def send_email(recepient, contents={}):
    
    # Create message container - the correct MIME type is multipart/alternative.
    msg = MIMEMultipart('alternative')
    msg['Subject'] = "Testing"
    msg['From'] = me
    msg['To'] = recepient

    # text = "Hi!\nHow are you?\nHere is the link you wanted:\nhttp://www.python.org"

    # load the html body
    with open(dirname + '/email_embedded.html', 'r') as f:
        html = f.read()

    
    # Record the MIME types of both parts - text/plain and text/html.
    # part1 = MIMEText(text, 'plain')
    part2 = MIMEText(html, 'html')

    # Attach parts into message container.
    # According to RFC 2046, the last part of a multipart message, in this case
    # the HTML message, is best and preferred.
    # msg.attach(part1)
    msg.attach(part2)

    # Send the message via local SMTP server.
    server = smtplib.SMTP('smtp.gmail.com:587')
    server.ehlo()
    server.starttls()
    username = me
    password = 'zhang647'
    server.login(username,password)
    server.sendmail(me, recepient, msg.as_string())
    server.quit()
    # sendmail function takes 3 arguments: sender's address, recipient's address
    # and message to send - here it is sent as one string.
    # server.sendmail(me, you, msg.as_string())

def invite():
    cmd = '''
          select p.url, p.email, posts.content, blogs_posts.blog_url from 
          (select url, email from profiles 
           where profiles.url not in (select profile_url from profiles_surveys) and email is not null
          ) as p, profiles_blogs, blogs_posts, posts 
          where p.url = profiles_blogs.profile_url and profiles_blogs.blog_url = blogs_posts.blog_url and blogs_posts.post_url = posts.url;
          '''

# send('renhzhang2@gmail.com')