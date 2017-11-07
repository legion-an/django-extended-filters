from django import forms
try:
    from django.shortcuts import reverse
except ImportError:
    from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from django.contrib.admin.widgets import AdminDateWidget
from django.contrib.admin.utils import get_fields_from_path, get_model_from_relation

from . import AUTOCOMPLETE


if AUTOCOMPLETE:
    from dal.autocomplete import ListSelect2, ModelSelect2


class DateRangeForm(forms.Form):

    def __init__(self, request, *args, **kwargs):
        self.request = request
        field_name = kwargs.pop('field_name')
        super(DateRangeForm, self).__init__(*args, **kwargs)

        self.fields['%s__gte' % field_name] = forms.DateField(
            label='',
            widget=AdminDateWidget(
                attrs={'placeholder': _('From date')}
            ),
            localize=True,
            required=False
        )

        self.fields['%s__lte' % field_name] = forms.DateField(
            label='',
            widget=AdminDateWidget(
                attrs={'placeholder': _('To date')}
            ),
            localize=True,
            required=False,
        )
        

if AUTOCOMPLETE:
    class AutocompleteForm(forms.Form):

        def __init__(self, request, model, field_path, *args, **kwargs):
            self.field_path = field_path
            value = kwargs.get('data').get(self.field_path)
            fields = get_fields_from_path(model, self.field_path)
            is_relation = fields[0].is_relation
            url = 'filter_model_autocomplete' if is_relation else 'filter_list_autocomplete'

            super(AutocompleteForm, self).__init__(*args, **kwargs)
            url = reverse(
                url,
                kwargs={
                    'app': model._meta.app_label,
                    'model': model._meta.model_name,
                    'field_path': self.field_path
                }
            )
            if request.GET:
                url = '%s?%s' % (url, request.GET.urlencode())

            if is_relation:
                related_model = get_model_from_relation(fields[-1])
                qs = related_model._default_manager.all()
                if value:
                    qs = qs.filter(pk=value)
                self.fields[self.field_path] = forms.ModelChoiceField(
                    queryset=qs, required=False, widget=ModelSelect2(url=url)
                )
            else:
                choices = [(value, value)] if value else []
                self.fields[self.field_path] = forms.ChoiceField(
                    choices=choices, required=False, widget=ListSelect2(url=url),
                )

        def field(self):
            return self[self.field_path]