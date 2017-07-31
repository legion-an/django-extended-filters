from django import forms
try:
    from django.shortcuts import reverse
except ImportError:
    from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from django.contrib.admin.templatetags.admin_static import static
from django.contrib.admin.widgets import AdminDateWidget
from django.contrib.admin.utils import get_fields_from_path
from django.utils import six

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

    @property
    def media(self):
        try:
            if getattr(self.request, 'daterange_filter_media_included'):
                return forms.Media()
        except AttributeError:
            setattr(self.request, 'daterange_filter_media_included', True)

            js = ["calendar.js", "admin/DateTimeShortcuts.js"]
            css = ['widgets.css']

            return forms.Media(
                js=[static("admin/js/%s" % path) for path in js],
                css={'all': [static("admin/css/%s" % path) for path in css]}
            )
        

if AUTOCOMPLETE:
    class AutocompleteForm(forms.Form):

        def __init__(self, *args, **kwargs):
            model = kwargs.pop('model')
            request = kwargs.pop('request')
            self.field_path = kwargs.pop('field_path')
            value = kwargs.get('data').get(self.field_path)
            fields = get_fields_from_path(model, self.field_path)
            url = 'filter_model_autocomplete' if fields[0].is_relation else 'filter_list_autocomplete'
            is_relation = url == 'filter_model_autocomplete'

            if value:
                choices = [(value, value)]
            else:
                choices = []

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
                self.fields[self.field_path] = forms.ModelChoiceField(
                    queryset=model._default_manager.none(), required=False, widget=ModelSelect2(url=url)
                )
            else:
                self.fields[self.field_path] = forms.ChoiceField(
                    choices=choices, required=False, widget=ListSelect2(url=url),
                )

        def field(self):
            return self[self.field_path]