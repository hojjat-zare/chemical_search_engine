from django.contrib import admin
from .models import *
from django.apps import apps
#################################### copy from django admin/options.py ######################
# import copy
# import json
# import operator
# import re
# from collections import OrderedDict
# from functools import partial, reduce, update_wrapper
#
# from django import forms
# from django.conf import settings
# from django.contrib import messages
# from django.contrib.admin import helpers, widgets
# from django.contrib.admin.checks import (
#     BaseModelAdminChecks, InlineModelAdminChecks, ModelAdminChecks,
# )
# from django.contrib.admin.exceptions import DisallowedModelAdminToField
# from django.contrib.admin.templatetags.admin_urls import add_preserved_filters
# from django.contrib.admin.utils import (
#     NestedObjects, construct_change_message, flatten_fieldsets,
#     get_deleted_objects, lookup_needs_distinct, model_format_dict, quote,
#     unquote,
# )
# from django.contrib.auth import get_permission_codename
# from django.core.exceptions import (
#     FieldDoesNotExist, FieldError, PermissionDenied, ValidationError,
# )
# from django.core.paginator import Paginator
# from django.db import models, router, transaction
# from django.db.models.constants import LOOKUP_SEP
# from django.db.models.fields import BLANK_CHOICE_DASH
# from django.forms.formsets import DELETION_FIELD_NAME, all_valid
# from django.forms.models import (
#     BaseInlineFormSet, inlineformset_factory, modelform_defines_fields,
#     modelform_factory, modelformset_factory,
# )
# from django.forms.widgets import CheckboxSelectMultiple, SelectMultiple
# from django.http import HttpResponseRedirect
# from django.http.response import HttpResponseBase
# from django.template.response import SimpleTemplateResponse, TemplateResponse
# from django.urls import reverse
# from django.utils import six
# from django.utils.decorators import method_decorator
# from django.utils.encoding import force_text, python_2_unicode_compatible
# from django.utils.html import format_html
# from django.utils.http import urlencode, urlquote
# from django.utils.safestring import mark_safe
# from django.utils.text import capfirst, format_lazy, get_text_list
# from django.utils.translation import ugettext as _, ungettext
# from django.views.decorators.csrf import csrf_protect
# from django.views.generic import RedirectView
#


##############################################################################################
# import pdb
TO_FIELD_VAR = '_to_field'
IS_POPUP_VAR = '_popup'
#################### register all models automatically #################
app = apps.get_app_config('search_in_database')
tables_with_multi_column_primary_key = ['entitiesrelatedphrases','entitiesalternatenames','entityrelationentity','entsblobpropsvalues','entsdoublepropsvalues','entsintegerpropsvalues','entsstringpropsvalues']
for model_name, model in app.models.items():
    if(not str(model_name) in tables_with_multi_column_primary_key):
        admin.site.register(model)
########################################################################
@admin.register(EntityRelationEntity)
class EntityRelationEntityAdmin(admin.ModelAdmin):
    # def save_model(self, request, obj, form, change):
    #     """
    #     Given a model instance save it to the database.
    #     """
    #     breakpoint()
    #     obj.save()

    def get_object(self, request, object_id, from_field=None):
        """
        overrided by hojjat
        Returns an instance matching the field and value provided, the primary
        key is used if no field is provided. Returns ``None`` if no match is
        found or the object_id fails validation.
        """
        queryset = self.get_queryset(request)
        model = queryset.model
        # field = model._meta.pk if from_field is None else model._meta.get_field(from_field)
        try:
            # breakpoint()
            # object_id = field.to_python(object_id)
            #######################################################################

            manuall_object_id = object_id.split('$')
            # return queryset.get(**{'eid1': manuall_object_id[0],'relationid':manuall_object_id[1] , 'eid2':manuall_object_id[2]})
            return queryset.get(**{'prop_owner_eid': manuall_object_id[0],'prop_eid':manuall_object_id[1] , 'drowid':manuall_object_id[2] ,})
            #######################################################################
        except (model.DoesNotExist, ValidationError, ValueError):
            return None

    def save_model(self, request, obj, form, change):
        """
        Given a model instance save it to the database.
        """
        primary_key_fields = self.model.get_primarykey_fields_name()
        primary_key = request.path.split('/')[4].split('$')
        # primary_key_fields.reverse()
        # primary_key.reverse()
        db_row_selector = dict(zip(primary_key_fields, primary_key))
        # for key in request.POST:
        #     if(key in self.model.get_primarykey_fields_name()):
        #         primary_key.append(request.POST[key])
        breakpoint()
        obj.save()

    def delete_model(self, request, obj):
        """
        Given a model instance delete it from the database.
        """
        breakpoint()
        obj.delete()
    # def _changeform_view(self, request, object_id, form_url, extra_context):
    #     to_field = request.POST.get(TO_FIELD_VAR, request.GET.get(TO_FIELD_VAR))
    #     if to_field and not self.to_field_allowed(request, to_field):
    #         raise DisallowedModelAdminToField("The field %s cannot be referenced." % to_field)
    #
    #     model = self.model
    #     opts = model._meta
    #
    #     if request.method == 'POST' and '_saveasnew' in request.POST:
    #         object_id = None
    #
    #     add = object_id is None
    #
    #     if add:
    #         if not self.has_add_permission(request):
    #             raise PermissionDenied
    #         obj = None
    #
    #     else:
    #         obj = self.get_object(request, unquote(object_id), to_field)
    #
    #         if not self.has_change_permission(request, obj):
    #             raise PermissionDenied
    #
    #         if obj is None:
    #             return self._get_obj_does_not_exist_redirect(request, opts, object_id)
    #
    #     ModelForm = self.get_form(request, obj)
    #     if request.method == 'POST':
    #         form = ModelForm(request.POST, request.FILES, instance=obj)
    #         if form.is_valid():
    #             form_validated = True
    #             new_object = self.save_form(request, form, change=not add)
    #         else:
    #             form_validated = False
    #             new_object = form.instance
    #         formsets, inline_instances = self._create_formsets(request, new_object, change=not add)
    #         if all_valid(formsets) and form_validated:
    #             breakpoint()
    #             self.save_model(request, new_object, form, not add)
    #             self.save_related(request, form, formsets, not add)
    #             change_message = self.construct_change_message(request, form, formsets, add)
    #             if add:
    #                 self.log_addition(request, new_object, change_message)
    #                 return self.response_add(request, new_object)
    #             else:
    #                 self.log_change(request, new_object, change_message)
    #                 return self.response_change(request, new_object)
    #         else:
    #             form_validated = False
    #     else:
    #         if add:
    #             initial = self.get_changeform_initial_data(request)
    #             form = ModelForm(initial=initial)
    #             formsets, inline_instances = self._create_formsets(request, form.instance, change=False)
    #         else:
    #             form = ModelForm(instance=obj)
    #             formsets, inline_instances = self._create_formsets(request, obj, change=True)
    #
    #     adminForm = helpers.AdminForm(
    #         form,
    #         list(self.get_fieldsets(request, obj)),
    #         self.get_prepopulated_fields(request, obj),
    #         self.get_readonly_fields(request, obj),
    #         model_admin=self)
    #     media = self.media + adminForm.media
    #
    #     inline_formsets = self.get_inline_formsets(request, formsets, inline_instances, obj)
    #     for inline_formset in inline_formsets:
    #         media = media + inline_formset.media
    #     my_title = ''
    #     if(add):
    #         my_title = 'Add '
    #     else:
    #         my_title = 'Change '
    #     my_title = my_title + force_text(opts.verbose_name)
    #     context = dict(
    #         self.admin_site.each_context(request),
    #         title=my_title,
    #         adminform=adminForm,
    #         object_id=object_id,
    #         original=obj,
    #         is_popup=(IS_POPUP_VAR in request.POST or
    #                   IS_POPUP_VAR in request.GET),
    #         to_field=to_field,
    #         media=media,
    #         inline_admin_formsets=inline_formsets,
    #         errors=helpers.AdminErrorList(form, formsets),
    #         preserved_filters=self.get_preserved_filters(request),
    #     )
    #
    #     # Hide the "Save" and "Save and continue" buttons if "Save as New" was
    #     # previously chosen to prevent the interface from getting confusing.
    #     if request.method == 'POST' and not form_validated and "_saveasnew" in request.POST:
    #         context['show_save'] = False
    #         context['show_save_and_continue'] = False
    #         # Use the change template instead of the add template.
    #         add = False
    #
    #     context.update(extra_context or {})
    #
    #     return self.render_change_form(request, context, add=add, change=not add, obj=obj, form_url=form_url)


admin.site.register(EntsIntegerPropsValues,EntityRelationEntityAdmin)
