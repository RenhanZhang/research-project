from django.shortcuts import render
#from django.template.loader import get_template
from django.http import HttpResponse
from django.template import Template, Context
import os
# Create your views here.

from Blogger_Retriever import get

def search_blog_by_link(request):
    #return render(request, 'search_page.html')
    if 'link' not in request.GET:
        return HttpResponse('Please input an valid url to the blog')

    blog_link = request.GET['link']
    blog, posts = get.get_blog_by_link(blog_link)
    
    context = {'blog_name': blog['name'], 'posts': posts}
    return render(request, 'blog_search_result.html', context)


