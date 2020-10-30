from django.contrib import admin
from .models import *
from django.apps import apps
# import pdb

#################### register all models automatically #################
app = apps.get_app_config('search_in_database')
for model_name, model in app.models.items():
    if(not str(model_name) in 'entities entityrelationentity'):
        admin.site.register(model)
########################################################################
@admin.register(EntityRelationEntity)
class EntityRelationEntityAdmin(admin.ModelAdmin):
    def get_object(self, request, object_id, from_field=None):
        """
        Returns an instance matching the field and value provided, the primary
        key is used if no field is provided. Returns ``None`` if no match is
        found or the object_id fails validation.
        """
        queryset = self.get_queryset(request)
        model = queryset.model
        field = model._meta.pk if from_field is None else model._meta.get_field(from_field)
        try:
            object_id = field.to_python(object_id)
            return queryset.get(**{field.name: object_id,'relationid':8 , 'eid2':110})
        except (model.DoesNotExist, ValidationError, ValueError):
            return None



class EntitiesAdmin(admin.ModelAdmin):
    # pass
    list_display = ('entid', 'mainname', 'enttypeid')
    fieldsets = (
        (None, {
            'fields': ('entid', 'mainname', 'enttypeid')
        }),
    )

admin.site.register(Entities,EntitiesAdmin)
# class ResultsAdmin(admin.ModelAdmin):
#     class Media:
#         css = {
#             'all': ('style.css',)
#         }
#
# admin.site.register(Results,ResultsAdmin)
