from django.contrib import admin
from .models import *
from django.apps import apps

##################### register all models automatically #################
app = apps.get_app_config('search_in_database')
for model_name, model in app.models.items():
    admin.site.register(model)
#######################################################################
