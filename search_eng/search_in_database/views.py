from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.urls import reverse
from .models import *

def index(request):
  return render(request, 'search_in_database/index.html')
