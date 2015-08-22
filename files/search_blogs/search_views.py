from django.shortcuts import render, render_to_response
#from django.template.loader import get_template
from django.http import HttpResponse
from django.template import Template, Context, RequestContext
from Blogger_Retriever import get
from TextVisualize import visualize
from DB_Handling import BlogsDB
import ipdb
import re, os

'''
def search_blog_by_link(request):
    
    #return render(request, 'search_page.html')
    if 'link' not in request.GET:
        return HttpResponse('Please input an valid url to the blog')

    blog_link = request.GET['link']
    profile, blog, posts = get.get_blog_by_link(blog_link)

    # update the database
    dbh = BlogsDB.BlogsDB_Handler()
    dbh.batch_update(profile, blog, posts)

    if blog is None:
        return HttpResponse('Please input a valid url')

    wvt_uri = visualize.words_vs_time(posts)
    wc_uri = visualize.word_cloud(posts)
    table = visualize.words_vs_time_beta(posts)
    ctx = Context({'table':table, 'posts': posts, 'blog_name': blog['name'].replace("\'", ''), 'wf_vs_time': wvt_uri, 'word_cloud':wc_uri})

    return render(request, 'blog_search_result.html', ctx)


    table = visualize.words_vs_time_beta(posts)
    ctx = Context({'table':table})
    return render(request, 'google_linechart.html', ctx)
    #return render_to_response('blog_search_result.html', {'posts': posts, 'blog_name': blog['name']},

'''
def search_blog_by_link(request):

    if 'link' not in request.GET:
        return HttpResponse('Please input a url to the blog')

    dbh = BlogsDB.BlogsDB_Handler()
    blog_link = request.GET['link']
    posts = dbh.get_posts_in_blog(blog_link)
    # ipdb.set_trace()
    if len(posts) == 0:
        latest = -1
    else:
        latest = posts[-1]['published']

    profile, blog, new_posts = get.get_blog_by_link(blog_link, latest)

    posts.extend(new_posts)

    if blog is None:
        return HttpResponse('Please input a valid url')

    if len(posts) == 0:
        return HttpResponse('Oops. Seems like you have published nothing in this blog')

    mask = 100 if len(posts) > 100 else len(posts)

    # visualization
    wc_uri = visualize.word_cloud(posts[-mask:])
    wf_vs_time = visualize.words_vs_time_beta(posts[-mask:])
    le_classes = visualize.ling_ethnography(posts[-mask:])
    ngram_model = visualize.ngram_model(posts[-mask:])

    # update the database
    dbh.batch_update(profile, blog, new_posts)


    ctx = Context({'posts': posts, 'blog_name': blog['name'].replace("\'", ''), 'ngram_model': ngram_model,\
                   'wf_vs_time': wf_vs_time, 'word_cloud':wc_uri, 'le_classes':le_classes})

    dbh.close()
    return render(request, 'blog_search_result.html', ctx)
