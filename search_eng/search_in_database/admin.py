from django.contrib import admin
from .models import *
from django.apps import apps

#################### register all models automatically #################
app = apps.get_app_config('search_in_database')
# tables_with_multi_column_primary_key = ['entitiesrelatedphrases','entitiesalternatenames','entityrelationentity','entsblobpropsvalues','entsdoublepropsvalues','entsintegerpropsvalues','entsstringpropsvalues']
for model_name, model in app.models.items():
    # if(not str(model_name) in tables_with_multi_column_primary_key):
    admin.site.register(model)
########################################################################
# @admin.register(EntityRelationEntity)
# class EntityRelationEntityAdmin(admin.ModelAdmin):
#     pass
#     # def save_model(self, request, obj, form, change):
#     #     """
#     #     Given a model instance save it to the database.
#     #     """
#     #     breakpoint()
#     #     obj.save(force_insert=True)
#
# admin.site.register(EntsIntegerPropsValues,EntityRelationEntityAdmin)
