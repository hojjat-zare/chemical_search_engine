from django.contrib import admin
from .models import *
from django.apps import apps
from django.contrib.admin.templatetags.admin_urls import add_preserved_filters
from django.contrib.admin.options import get_content_type_for_model
from django.template.response import TemplateResponse
IS_POPUP_VAR = '_popup'
TO_FIELD_VAR = '_to_field'
#################### register all models automatically #################
app = apps.get_app_config('search_in_database')
# tables_with_multi_column_primary_key = ['entitiesrelatedphrases','entitiesalternatenames','entityrelationentity','entsblobpropsvalues','entsdoublepropsvalues','entsintegerpropsvalues','entsstringpropsvalues']
for model_name, model in app.models.items():
    if(not str(model_name) in ['results','entsblobpropsvalues']):
        admin.site.register(model)
########################################################################

class Has_blob_field_Admin(admin.ModelAdmin):
    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        opts = self.model._meta
        app_label = opts.app_label
        preserved_filters = self.get_preserved_filters(request)
        form_url = add_preserved_filters({'preserved_filters': preserved_filters, 'opts': opts}, form_url)
        view_on_site_url = self.get_view_on_site_url(obj)
        context.update({
            'add': add,
            'change': change,
            'has_add_permission': self.has_add_permission(request),
            'has_change_permission': self.has_change_permission(request, obj),
            'has_delete_permission': self.has_delete_permission(request, obj),
            'has_file_field': True,  # FIXME - this should check if form or formsets have a FileField,
            'has_absolute_url': view_on_site_url is not None,
            'absolute_url': view_on_site_url,
            'form_url': form_url,
            'opts': opts,
            'content_type_id': get_content_type_for_model(self.model).pk,
            'save_as': self.save_as,
            'save_on_top': self.save_on_top,
            'to_field_var': TO_FIELD_VAR,
            'is_popup_var': IS_POPUP_VAR,
            'app_label': app_label,
        })
        if add and self.add_form_template is not None:
            form_template = self.add_form_template
        else:
            form_template = self.change_form_template

        request.current_app = self.admin_site.name
        ###### add to context some information to show pictures
        request_url = request.path
        request_url = request_url.split('/')
        if(request_url[len(request_url)-2]=='change'):
            row_pk = request_url[4]
            result_blob = self.model.objects.get(pk=row_pk).scheme_image_tag(width=500,height=300)
            context['manual_file_field'] = result_blob
        else:
            context['manual_file_field'] = ''
        return TemplateResponse(request, form_template or [
            "admin/%s/%s/change_form.html" % (app_label, opts.model_name),
            "admin/%s/change_form.html" % app_label,
            "admin/change_form.html"
        ], context)


@admin.register(Results)
class ResultsAdmin(Has_blob_field_Admin):
    list_display = ('get_search_ref','mimetype','scheme_image_tag')
    fieldsets = (
        (None, {
            'fields': ('searchid','mimetype','result')
        }),

    )

@admin.register(EntsBlobPropsValues)
class EntsBlobPropsValuesAdmin(Has_blob_field_Admin):
    list_display = ('__str__','mimetype','scheme_image_tag')
    # fieldsets = (
    #     (None, {
    #         'fields': ('prop_owner_eid','prop_eid','drowid','mimetype','dvalue')
    #     }),
    #
    # )
# admin.site.register(EntsBlobPropsValues,EntsBlobPropsValuesAdmin)
