from django.shortcuts import render
#from django.template.loader import get_template
from django.http import HttpResponse
from django.template import Template, Context
import os
# Create your views here.

from Blogger_Retriever import get
from TextVisualize import visualize

def search_blog_by_link(request):
    #return render(request, 'search_page.html')
    if 'link' not in request.GET:
        return HttpResponse('Please input an valid url to the blog')

    blog_link = request.GET['link']
    blog, posts = get.get_blog_by_link(blog_link)

    visualize.words_vs_time(posts)

    return HttpResponse(request, 'done')


