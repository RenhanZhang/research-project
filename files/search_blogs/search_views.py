from django.shortcuts import render, render_to_response
#from django.template.loader import get_template
from django.http import HttpResponse
from django.template import Template, Context, RequestContext

import os
# Create your views here.
import requests
from Blogger_Retriever import get
from TextVisualize import visualize
import ipdb
def search_blog_by_link(request):
    
    #return render(request, 'search_page.html')
    if 'link' not in request.GET:
        return HttpResponse('Please input an valid url to the blog')

    blog_link = request.GET['link']
    blog, posts = get.get_blog_by_link(blog_link)
    if blog is None:
        return HttpResponse('Please input a valid url')
    
    uri = visualize.words_vs_time(posts)
    
    #ipdb.set_trace()
    ctx = Context({'posts': posts, 'blog_name': blog['name'], 'inline_png': uri})
    return render(request, 'blog_search_result.html', ctx)
    #return render_to_response('blog_search_result.html', {'posts': posts, 'blog_name': blog['name']},
