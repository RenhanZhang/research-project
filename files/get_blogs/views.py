from django.shortcuts import render
#from django.template.loader import get_template
from django.http import HttpResponse
from django.template import Template, Context
import os
# Create your views here.

def search(request):
    #return render(request, 'search_page.html')
    return HttpResponse('Please submit a search term.')
