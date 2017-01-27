import json

from django import http
from django.apps import apps
from django.utils.http import urlencode
from django.utils import six
from django.db.models import Model
from django.contrib.admin.utils import get_fields_from_path

from dal.autocomplete import Select2ListView


def get_query_string(params, new_params=None, remove=None):
    if new_params is None:
        new_params = {}
    if remove is None:
        remove = []
    p = params.copy()
    for r in remove:
        for k in list(p):
            if k.startswith(r):
                del p[k]
    for k, v in new_params.items():
        if v is None:
            if k in p:
                del p[k]
        else:
            p[k] = v
    return '?%s' % urlencode(sorted(p.items()))


class FilterListAutocomplete(Select2ListView):

    def get_choices(self, qs, field_path):
        return sorted(set(qs.values_list(field_path, flat=True)))

    def get_relation_choices(self, field, qs, field_path):
        return field.related_model.objects.filter(pk__in=qs.values(field_path)).distinct()

    def get_result_label(self, result):
        return six.text_type(result)

    def get_result_value(self, result, field_path, query_string):
        return '%s&%s=%s' % (query_string, field_path, result.pk if isinstance(result, Model) else result)

    def get_queryset(self, Model, field_path):
        return Model._default_manager.exclude(**{'%s__isnull' % field_path: True})

    def get(self, request, app, model, field_path, *args, **kwargs):
        """"Return option list json response."""
        Model = apps.get_model(app, model)
        field = get_fields_from_path(Model, field_path)[-1]
        qs = self.get_queryset(Model, field_path)
        if field.is_relation:
            results = self.get_relation_choices(field, qs, field_path)
            if self.q:
                results = results.filter(**{'pk': self.q})
        else:
            results = self.get_choices(qs, field_path)
            if self.q:
                results = [x for x in results if self.q in x]

        query_string = get_query_string(request.GET, remove=[field_path])
        return http.HttpResponse(json.dumps({
            'results': [dict(id=self.get_result_value(x, field_path, query_string), text=self.get_result_label(x))
                        for x in results]
        }))

    def post(self, request):
        raise http.Http404