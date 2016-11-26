import datetime

from django.utils.encoding import smart_text
from django.db.models.fields.related import ForeignKey, ManyToManyField
from django.contrib import admin
from django.contrib.admin.options import IncorrectLookupParameters
from django.conf import settings
from django.forms import ValidationError

from .forms import DateRangeForm

MPTT = False
if 'mptt' in settings.INSTALLED_APPS:
    from mptt.forms import TreeNodeChoiceField
    MPTT = True


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


class TreeRelatedFieldListFilter(admin.RelatedFieldListFilter):

    def field_choices(self, field, request, model_admin):
        if not MPTT:
            raise NotImplementedError("you need to install mptt module and add it to INSTALLED_APPS")
        form_field = TreeNodeChoiceField(queryset=field.related_model.objects.all(), empty_label=None)
        return form_field.choices


class TreeDescendantsRelatedFieldListFilter(TreeRelatedFieldListFilter):

    def queryset(self, request, queryset):
        used_parameters = self.used_parameters.copy()
        if self.lookup_kwarg in used_parameters:
            field_path = self.lookup_kwarg.rstrip('__exact').split('__')
            item = self.field.related_model.objects.get(**{'id': used_parameters[self.lookup_kwarg]})
            if not item.is_leaf_node():
                del used_parameters[self.lookup_kwarg]
                key = '%s__in' % '__'.join(f for f in field_path)
                used_parameters[key] = item.get_descendants(include_self=True).values('id')
        try:
            return queryset.filter(**used_parameters)
        except ValidationError as e:
            raise IncorrectLookupParameters(e)