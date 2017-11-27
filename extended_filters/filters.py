import datetime

from django.utils.encoding import smart_text
from django.utils.http import urlencode
from django.db.models.fields.related import ForeignKey, ManyToManyField
from django.contrib import admin
from django.contrib.admin.templatetags.admin_static import static
from django.contrib.admin.options import IncorrectLookupParameters
from django.contrib.admin.utils import prepare_lookup_value
from django.contrib.admin.sites import site
from django import forms

from .forms import DateRangeForm
from . import MPTT, AUTOCOMPLETE

if MPTT:
    from mptt.forms import TreeNodeChoiceField

if AUTOCOMPLETE:
    from .forms import AutocompleteForm


class FilterMediaMixin:
    media_attr = 'extended_filters_media_included'

    def __init__(self, *args, **kwargs):
        super(FilterMediaMixin, self).__init__(*args, **kwargs)
        if len(args) == 4:
            self.request = args[0]
        else:
            self.request = args[1]

    @property
    def js(self):
        return (
            'extended_filters/js/scripts.js',
            "admin/js/calendar.js",
            "admin/js/admin/DateTimeShortcuts.js",
        )

    @property
    def css(self):
        return ('admin/css/widgets.css',)

    @property
    def media(self):
        try:
            if getattr(self.request, self.media_attr):
                return forms.Media()
        except AttributeError:
            setattr(self.request, self.media_attr, True)
            return forms.Media(
                js=[static(path) for path in self.js],
                css={'all': [static(path) for path in self.css]}
            )


class DateRangeFilter(FilterMediaMixin, admin.filters.FieldListFilter):
    template = 'extended_filters/date_range_filter.html'

    def __init__(self, field, request, params, model, model_admin, field_path):
        self.lookup_kwarg_since = '%s__gte' % field_path
        self.lookup_kwarg_upto = '%s__lte' % field_path
        super(DateRangeFilter, self).__init__(
            field, request, params, model, model_admin, field_path)
        self.form = self.get_form(request)
        data = request.GET.copy()
        data.pop(self.lookup_kwarg_since, None)
        data.pop(self.lookup_kwarg_upto, None)
        self.query_string = '?%s' % urlencode(sorted(data.items()))

    def choices(self, cl):
        yield {}

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
        return queryset


class CheckBoxFilterMixin(FilterMediaMixin):
    template = 'extended_filters/checkbox_filter.html'

    def setup(self, request, model_admin, field=None, field_path=None):
        if field:
            assert field_path
            if isinstance(field, (ForeignKey, ManyToManyField)):
                rel_name = field.rel.get_related_field().name
                self.lookup_kwarg = '%s__%s__in' % (field_path, rel_name)
                self.lookup_choices = self.field_choices(field, request, model_admin)
            else:
                self.lookup_kwarg = '%s__in' % field_path
                self.lookup_choices = self.field.flatchoices or \
                                      field.model.objects.all().distinct().values_list(field.name, field.name)
        else:
            self.lookup_kwarg = self.parameter_name

        self.lookup_val = request.GET.get(self.lookup_kwarg, '')
        data = request.GET.copy()
        data.pop(self.lookup_kwarg, None)
        self.query_string = '?%s' % urlencode(sorted(data.items()))

    def field_choices(self, field, request, model_admin):
        return field.get_choices(include_blank=False)

    def choices(self, cl):
        for lookup, title in self.lookup_choices:
            yield {
                'selected': smart_text(lookup) in self.lookup_val.split(',') if self.lookup_val else False,
                'display': title,
                'value': lookup,
            }
            
    def expected_parameters(self):
        return [self.lookup_kwarg]


class CheckBoxSimpleFilter(CheckBoxFilterMixin, admin.SimpleListFilter):
    def __init__(self, request, params, model, model_admin):
        self.setup(request, model_admin)
        super(CheckBoxSimpleFilter, self).__init__(request, params, model, model_admin)

    def value(self):
        value = self.used_parameters.get(self.parameter_name)
        return value.split(',') if value else []


class CheckBoxListFilter(CheckBoxFilterMixin, admin.FieldListFilter):
    def __init__(self, field, request, params, model, model_admin, field_path):
        self.setup(request, model_admin, field, field_path)
        super(CheckBoxListFilter, self).__init__(field, request, params, model, model_admin, field_path)


if MPTT:
    class TreeRelatedFilter(FilterMediaMixin, admin.RelatedFieldListFilter):

        def field_choices(self, field, request, model_admin):
            form_field = TreeNodeChoiceField(queryset=field.related_model.objects.all(), empty_label=None)
            return form_field.choices


    class TreeDescendantsFilter(TreeRelatedFilter):

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
            except forms.ValidationError as e:
                raise IncorrectLookupParameters(e)


if AUTOCOMPLETE:
    class BaseAutocompleteFilter(FilterMediaMixin):
        template = 'extended_filters/autocomplete_filter.html'
        lookup_kwarg = None
        media_attr = 'dal_filter_media_included'

        def __init__(self, field, request, params, model, model_admin, field_path):
            super().__init__(field, request, params, model, model_admin, field_path)
            self.lookup_kwarg = field_path.replace('__id__exact', '')
            self.params = dict(request.GET.items())
            for p in self.expected_parameters():
                if p in params:
                    value = params.pop(p)
                    self.used_parameters[p] = prepare_lookup_value(p, value)

            autocomplete_fields = getattr(site._registry.get(model), 'autocomplete_fields', None)
            if not autocomplete_fields or not autocomplete_fields.get(field_path):
                raise NotImplementedError("You must setup autocomplete fields")

            self.form = self.get_form(request, field, field_path, model)

        def get_form(self, request, field, field_path, model):
            return AutocompleteForm(request=request, model=model, field_path=field_path, data=self.used_parameters)

        def expected_parameters(self):
            return [self.lookup_kwarg]

        def choices(self, cl):
            return []

        @property
        def js(self):
            return (
                'autocomplete_light/jquery.init.js',
                'autocomplete_light/autocomplete.init.js',
                'autocomplete_light/vendor/select2/dist/js/select2.full.js',
                'autocomplete_light/forward.js',
                'autocomplete_light/select2.js',
                'extended_filters/js/autocomplete_script.js'
            )

        @property
        def css(self):
            return (
                'autocomplete_light/vendor/select2/dist/css/select2.css',
                'autocomplete_light/select2.css',
                'extended_filters/css/autocomplete_filters.css'
            )


    class AutocompleteFilter(BaseAutocompleteFilter, admin.FieldListFilter): pass


if MPTT and AUTOCOMPLETE:

    class TreeDescendantsAutocompleteFilter(BaseAutocompleteFilter, TreeDescendantsFilter): pass