from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.urls import reverse
from .models import *
from .tools import SentenceRelatedEntities,AllPropertiesOfEntity,PropertyOfEntity,get_result_for_search, get_result_for_entity
from .scraping import Search_methods

def index(request):
    return render(request, 'search_in_database/index.html')

def search_result(request):
    results = get_result_for_search(request.GET['q'])
    return render(request,'search_in_database/search_result.html',{'results':results})

def get_exact_entity(request,entity_mainname):
    results = get_result_for_entity(entity_mainname)
    return render(request,'search_in_database/search_result.html',{'results':results})
