from django.contrib import admin
from .models import *
from django.apps import apps
from django.contrib.admin.templatetags.admin_urls import add_preserved_filters
from django.contrib.admin.options import get_content_type_for_model
from django.template.response import TemplateResponse
IS_POPUP_VAR = '_popup'
TO_FIELD_VAR = '_to_field'
from django.urls import reverse
from django.utils.http import urlencode
from .tools import PropertyOfEntity
from django.utils.text import (
    capfirst, format_lazy, get_text_list, smart_split, unescape_string_literal,
)
from functools import reduce
import operator
from django.contrib.admin.utils import lookup_needs_distinct
id_of_has = 8
id_of_component = 89
id_of_is_instance_of = 9
dependent_instance = 7
id_of_pahse = 260
id_of_antoin = 275
id_of_ideal_heat_cap = 343
id_of_specific_props = 291
id_of_heat_capacity_coefficients_for_ideal_gas = 344
id_of_component_antoin_coefficients = 271

#################### register all models automatically #################
app = apps.get_app_config('search_in_database')
# tables_with_multi_column_primary_key = ['entitiesrelatedphrases','entitiesalternatenames','entityrelationentity','entsblobpropsvalues','entsdoublepropsvalues','entsintegerpropsvalues','entsstringpropsvalues']
for model_name, model in app.models.items():
    if(not str(model_name) in ['results','entsblobpropsvalues','entityrelationentity','entities','entsdoublepropsvalues','entsintegerpropsvalues','entsstringpropsvalues']):
        admin.site.register(model)
########################################################################

class Has_blob_field_Admin(admin.ModelAdmin):
    #override
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
            result_blob = self.model.objects.get(pk=row_pk).blob_value(width=500,height=300)
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
    list_display = ('get_search_ref','mimetype','blob_value')
    fieldsets = (
        (None, {
            'fields': ('searchid','mimetype','result')
        }),

    )

@admin.register(EntsBlobPropsValues)
class EntsBlobPropsValuesAdmin(Has_blob_field_Admin):
    list_display = ('__str__','mimetype','blob_value')


@admin.register(Entities)
class EntitiesAdmin(admin.ModelAdmin):
    list_display = ('mainname','enttypeid')
    search_fields = ('mainname',)


class HasExactSearchWithQuotation(admin.ModelAdmin):

    def get_search_results(self, request, queryset, search_term):
        """
        Returns a tuple containing a queryset to implement the search,
        and a boolean indicating if the results may contain duplicates.
        """
        # Apply keyword searches.
        def construct_search(field_name):
            if field_name.startswith('^'):
                return "%s__istartswith" % field_name[1:]
            elif field_name.startswith('='):
                return "%s__iexact" % field_name[1:]
            elif field_name.startswith('@'):
                return "%s__search" % field_name[1:]
            else:
                return "%s__icontains" % field_name

        use_distinct = False
        search_fields = self.get_search_fields(request)
        if search_fields and search_term:
            orm_lookups = [construct_search(str(search_field))
                           for search_field in search_fields]
            for bit in smart_split(search_term):
                if bit.startswith(('"', "'")):
                    bit = unescape_string_literal(bit)
                or_queries = [models.Q(**{orm_lookup: bit})
                              for orm_lookup in orm_lookups]
                queryset = queryset.filter(reduce(operator.or_, or_queries))
            if not use_distinct:
                for search_spec in orm_lookups:
                    if lookup_needs_distinct(self.opts, search_spec):
                        use_distinct = True
                        break

        return queryset, use_distinct

@admin.register(EntityRelationEntity)
class EntityRelationEntityAdmin(HasExactSearchWithQuotation):
    list_display = ('get_eid1','link_to_property','get_eid2')
    search_fields = ('^eid1__mainname', )

    def link_to_property(self,obj):
        from django.utils.html import format_html
        if(obj.relationid_id == id_of_has):
            table_name = PropertyOfEntity(obj.eid1,obj.eid2).get_table_name_of_property()
            url = (reverse('admin:search_in_database_{}_changelist'.format(table_name))+ '?q="{}"'.format(obj.eid1.mainname))
            return format_html('<a href="{}">has</a>', url)
        return obj.get_relationid()
    link_to_property.short_description = "show_all_props"
    link_to_property.admin_order_field = 'relationid'

    def save_model(self, request, obj, form, change):
        """
        Given a model instance save it to the database.
        """
        obj.save()
        if(obj.relationid_id == id_of_is_instance_of and obj.eid2_id == id_of_component):
            phase,isCreated = Entities.objects.get_or_create(mainname='{} room phase'.format(obj.eid1.mainname),enttypeid_id=dependent_instance)
            antoin ,isCreated= Entities.objects.get_or_create(mainname='{} antoin coefficients'.format(obj.eid1.mainname),enttypeid_id=dependent_instance)
            heatcap ,isCreated= Entities.objects.get_or_create(mainname='{} heat cap coefficients'.format(obj.eid1.mainname),enttypeid_id=dependent_instance)
            EntityRelationEntity.objects.get_or_create(eid1=antoin,relationid_id=id_of_drived_from,eid2_id=id_of_component_antoin_coefficients)
            EntityRelationEntity.objects.get_or_create(eid1=heatcap,relationid_id=id_of_drived_from,eid2_id=id_of_heat_capacity_coefficients_for_ideal_gas)
            EntsIntegerPropsValues.objects.filter(prop_owner_eid=obj.eid1,prop_eid_id=id_of_pahse,drowid=0).update(dvalue=phase.entid)
            EntsIntegerPropsValues.objects.filter(prop_owner_eid=obj.eid1,prop_eid_id=id_of_antoin,drowid=0).update(dvalue=antoin.entid)
            EntsIntegerPropsValues.objects.filter(prop_owner_eid=obj.eid1,prop_eid_id=id_of_ideal_heat_cap,drowid=0).update(dvalue=heatcap.entid)

@admin.register(EntsDoublePropsValues)
class EntsDoublePropsValuesAdmin(HasExactSearchWithQuotation):
    list_display = ('get_prop_owner_eid_mainname','get_prop_eid_mainname','drowid','dvalue')
    search_fields = ('^prop_owner_eid__mainname',)
    # raw_id_fields = ("prop_owner_eid",)

@admin.register(EntsStringPropsValues)
class EntsStringPropsValuesAdmin(HasExactSearchWithQuotation):
    list_display = ('get_prop_owner_eid_mainname','get_prop_eid_mainname','drowid','dvalue')
    search_fields = ('^prop_owner_eid__mainname',)

@admin.register(EntsIntegerPropsValues)
class EntsIntegerPropsValuesAdmin(HasExactSearchWithQuotation):
    list_display = ('get_prop_owner_eid_mainname','get_prop_eid_mainname','drowid','get_dvalue_equivalent_entity_if_exist')
    search_fields = ('^prop_owner_eid__mainname',)
