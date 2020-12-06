import os
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect, HttpResponse
from django.http import HttpResponse
from django.urls import reverse
from .models import *
from .tools import SentenceRelatedEntities, AllPropertiesOfEntity, PropertyOfEntity, get_result_for_search, \
    get_result_for_entity
from .scraping import Search_methods
import fdb
import threading
from time import time

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_BASE_DIR = os.path.join(BASE_DIR, "SEDB.FDB")


def index(request):
    return render(request, 'search_in_database/index.html')


def search_result(request):
    results = get_result_for_search(request.GET['q'].lower())
    return render(request, 'search_in_database/search_result.html', {'results': results})


def exact_entity(request, entity_mainname):
    results = get_result_for_entity(entity_mainname)
    # a = get_result_for_entity(">C=O (none-ring)")
    # breakpoint()
    return render(request, 'search_in_database/search_result.html', {'results': results})


def exact_entity_tree_mode(request, entity_mainname):
    results = get_result_for_entity(entity_mainname)
    return render(request, 'search_in_database/exact_result.html', {'results': results})


def get_scrapy_search(request):
    t1 = time()
    phrase = request.GET['entity']
    phrase = phrase.replace(" ", "#")
    do_download_images = request.GET['do_download_images']  ################################# add this setting to spider
    con = fdb.connect(dsn=DATA_BASE_DIR, user='SYSDBA', password='masterkey')
    cur = con.cursor()
    cur.execute('select gen_id(SEARCHS_SEARCHID_GEN, 1)from rdb$database;')
    search_id = cur.fetchone()[0];
    words_to_search = request.GET['properties']
    words_to_search = words_to_search.split(",")
    words_to_search = [word.strip() for word in words_to_search]

    words_to_search = [word.replace(" ", "#") for word in words_to_search]
    WTS = " ".join(words_to_search)
    # #means white space (means words come respectively after each other)
    # - or & means words that must be in the tag string or tag text not respectively
    path = os.path.join(BASE_DIR, 'search_in_database')
    inputs = "python spider.py {} {} {} {}".format(phrase, str(search_id), str('False'), WTS)
    os.system("cd " + path + " && " + inputs)
    blob_results = Results.objects.filter(searchid=search_id).order_by('resultid')
    results = []
    for blob in blob_results:
        results.append(blob.blob_value('auto', 'auto'))
    t2 = time()
    print("it takes about: ", t2 - t1, "seconds")
    inputs = "python spider.py {} {} {} {}".format(phrase, str(search_id), str('True'), WTS)
    # threading.Thread(target=os.system,args=("cd " + path + " && " + inputs,)).start()
    return render(request, 'search_in_database/scrapy_result.html', {'results': results})


def crawler_form(request):
    return render(request, 'search_in_database/crawler_form.html')
