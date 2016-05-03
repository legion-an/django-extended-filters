import datetime

from django.utils.encoding import smart_text
from django.db.models.fields.related import ForeignKey, ManyToManyField
from django.contrib import admin

from .forms import DateRangeForm


class DateRangeFilter(admin.filters.FieldListFilter):
    template = 'extended_filters/date_range_filter.html'

    def __init__(self, field, request, params, model, model_admin, field_path):
        self.lookup_kwarg_since = '%s__gte' % field_path
        self.lookup_kwarg_upto = '%s__lte' % field_path
        super(DateRangeFilter, self).__init__(
            field, request, params, model, model_admin, field_path)
        self.form = self.get_form(request)

    def choices(self, cl):
        yield {'query_string': cl.get_query_string({}, remove=[self.lookup_kwarg_since, self.lookup_kwarg_upto])}

    def expected_parameters(self):
        return [self.lookup_kwarg_since, self.lookup_kwarg_upto]

    def get_form(self, request):
        return DateRangeForm(request, data=self.used_parameters,
                             field_name=self.field_path)

    def queryset(self, request, queryset):
        if self.form.is_valid():
            # get no null params
            filter_params = dict(filter(lambda x: bool(x[1]), self.form.cleaned_data.items()))

            # filter by upto included
            lookup_upto = self.lookup_kwarg_upto
            if filter_params.get(lookup_upto) is not None:
                lookup_kwarg_upto_value = filter_params.pop(lookup_upto)
                filter_params['%s__lt' % self.field_path] = lookup_kwarg_upto_value + datetime.timedelta(days=1)

            return queryset.filter(**filter_params)
        else:
            return queryset


class CheckBoxListFilter(admin.ChoicesFieldListFilter):
    template = 'extended_filters/checkbox_filters.html'

    def __init__(self, field, request, params, model, model_admin, field_path):
        super(CheckBoxListFilter, self).__init__(
            field, request, params, model, model_admin, field_path)
        if self.field.flatchoices:
            self.lookup_kwarg = '%s__in' % field_path
            self.lookup_choices = self.field.flatchoices
        elif isinstance(field, ForeignKey) or isinstance(field, ManyToManyField):
            rel_name = field.rel.get_related_field().name
            self.lookup_kwarg = '%s__%s__in' % (field_path, rel_name)
            self.lookup_choices = self.field_choices(field, request, model_admin)
        else:
            self.lookup_kwarg = '%s__in' % field_path
            self.lookup_choices = field.model.objects.all().distinct().values_list(field.name, field.name)

        self.lookup_val = request.GET.get(self.lookup_kwarg, '')

    def expected_parameters(self):
        return [self.lookup_kwarg]

    def field_choices(self, field, request, model_admin):
        return field.get_choices(include_blank=False)

    def choices(self, cl):
        for lookup, title in self.lookup_choices:
            yield {
                'selected': smart_text(lookup) in self.lookup_val.split(','),
                'query_string': cl.get_query_string({}, remove=[self.lookup_kwarg]),
                'display': title,
                'value': lookup,
                'field': self.lookup_kwarg,
            }