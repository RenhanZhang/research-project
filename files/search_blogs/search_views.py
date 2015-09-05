from django.shortcuts import render, render_to_response
#from django.template.loader import get_template
from django.http import HttpResponse
from django.template import Template, Context, RequestContext
from Blogger_Retriever import get
from TextVisualize import visualize
from DB_Handling import BlogsDB
import ipdb
import re, os
import multiprocessing as mp

dirname = os.path.dirname(os.path.abspath(__file__))

def search_blog_by_link(request):

    if 'link' not in request.GET:
        return HttpResponse('Please input a url to the blog')

    dbh = BlogsDB.BlogsDB_Handler()
    blog_link = request.GET['link']
    MAX_TO_DISPLAY = int(request.GET['num_posts'])
    MAX_TO_DISPLAY = min(MAX_TO_DISPLAY, 200)

    posts = dbh.get_posts_in_blog(blog_link)

    # ipdb.set_trace()
    if len(posts) == 0:
        latest = -1
    else:
        latest = posts[-1]['published']

    profile, blog, new_posts, next_page_token = get.get_blog_by_link(blog_link, latest, MAX_TO_DISPLAY)

    if blog is None:
        return HttpResponse('Please input a valid Blogger url')
    
    if 'image_url' not in profile:
        # save profile and its blogs when failing to scrape it right now
        save_profile(profile['url'], blog['url'])

    posts.extend(new_posts)

    if len(posts) == 0:
        return HttpResponse('Oops. Seems like you have published nothing in this blog')
    
    mask = MAX_TO_DISPLAY if len(posts) > MAX_TO_DISPLAY else len(posts)
    
    ctx = {'blog_name': blog['name'].replace("\'", '')}

    # visualization
    ctx['wf_vs_month'] = visualize.words_vs_time(posts=posts[-mask:], freq_words=[], group_by='month')
    ctx['wf_vs_year'] = visualize.words_vs_time(posts=posts[-mask:], freq_words=[], group_by='year')
    ctx['wf_vs_week'] = visualize.words_vs_time(posts=posts[-mask:], freq_words=[], group_by='week')
    ctx['wf_vs_day'] = visualize.words_vs_time(posts=posts[-mask:], freq_words=[], group_by='day')

    #personality_url = visualize.peronality(posts[-mask:])
    #ctx['personality_url'] = personality_url

    ctx['word_cloud'] = visualize.word_cloud(posts[-mask:])
    
    ctx['le_classes'] = visualize.ling_ethnography(posts[-mask:])

    ctx['ngram_model'] = visualize.ngram_model(posts[-mask:])

    # update the database
    dbh.batch_update(profile, blog, new_posts)

    # spawn a parallel process the retrieve the remaining posts
    if next_page_token:
        proc = mp.Process(target=get.get_remain_posts,
                          args=(blog_link, blog['id'], next_page_token, get.MAX_TO_DISPLAY - len(posts), latest))
        proc.start()

    ctx = Context(ctx)

    dbh.close()
    return render(request, 'blog_search_result.html', ctx)

def save_profile(p_url, b_url):
    with open(os.path.dirname(dirname) + '/Blogger_Retriever/profile_to_scrape.txt', 'a') as f:
        f.write('%s, %s\n' % (p_url, b_url))
    

