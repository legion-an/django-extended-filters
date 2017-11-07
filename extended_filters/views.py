import json

from django import http
from django.apps import apps
from django.utils.http import urlencode
from django.utils import six
from django.db.models import Model, Q
from django.contrib.admin.sites import site
from django.contrib.admin.utils import get_fields_from_path, get_model_from_relation

from dal.autocomplete import Select2ListView, Select2QuerySetView


def get_query_string(params, remove=None):
    if remove is None:
        remove = []
    p = params.copy()
    for r in remove:
        p.pop(r, None)
    return '?%s' % urlencode(sorted(p.items()))


class BaseAutocomplete:

    def get_model(self, app, model):
        return apps.get_model(app, model)

    def get_result_label(self, result):
        return six.text_type(result)

    def get_result_value(self, result, field_path, query_string):
        return '%s&%s=%s' % (query_string, field_path, result.pk if isinstance(result, Model) else result)


class FilterListAutocomplete(Select2ListView, BaseAutocomplete):

    def get_choices(self, qs, field_path):
        return sorted(set(qs.values_list(field_path, flat=True)))

    def get(self, request, app, model, field_path, *args, **kwargs):
        """"Return option list json response."""
        Model = self.get_model(app, model)
        qs = Model._default_manager.exclude(**{'%s__isnull' % field_path: True})
        results = self.get_choices(qs, field_path)
        if self.q:
            results = [x for x in results if self.q in str(x)]  # result can be an integer

        query_string = get_query_string(request.GET, remove=[field_path, 'q'])
        return http.HttpResponse(json.dumps({
            'results': [dict(id=self.get_result_value(x, field_path, query_string), text=self.get_result_label(x))
                        for x in results]
        }))

    def post(self, request):
        raise http.Http404


class FilterModelAutocomplete(BaseAutocomplete, Select2QuerySetView):

    def get_queryset(self):
        qs = self.related_model._default_manager.all()
        lookup = site._registry.get(self.model).autocomplete_fields[self.field_path]
        if self.q:
            qojb = Q()
            for field in lookup:
                qojb.add(Q(**{field: self.q}), Q.OR)
            qs = qs.filter(qojb)
        return qs

    def get_results(self, context):
        return [
            {
                'id': self.get_result_value(result, self.field_path, self.query_string),
                'text': self.get_result_label(result),
            } for result in context['object_list']
        ]

    def get(self, request, app, model, field_path, *args, **kwargs):
        self.model = self.get_model(app, model)
        self.fields = get_fields_from_path(self.model, field_path)
        self.related_model = get_model_from_relation(self.fields[-1])
        self.field_path = field_path
        self.query_string = get_query_string(request.GET, remove=[field_path, 'q'])
        return super(FilterModelAutocomplete, self).get(request, *args, **kwargs)
