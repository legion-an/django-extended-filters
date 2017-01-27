from django import forms
from django.shortcuts import reverse
from django.utils.translation import ugettext as _
from django.contrib.admin.templatetags.admin_static import static
from django.contrib.admin.widgets import AdminDateWidget
from django.utils import six

from . import AUTOCOMPLETE


if AUTOCOMPLETE:
    from dal.autocomplete import ListSelect2, ListSelect2


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
            field = kwargs.pop('field')
            model = kwargs.pop('model')
            request = kwargs.pop('request')
            self.field_path = kwargs.pop('field_path')
            value = kwargs.get('data').get(self.field_path)
            if value and field.is_relation:
                self.choices = [(value, six.text_type(field.related_model.objects.get(pk=value)))]
            elif value:
                self.choices = [(value, value)]
            else:
                self.choices = []

            super(AutocompleteForm, self).__init__(*args, **kwargs)
            url = reverse(
                'filter_list_autocomplete',
                kwargs={
                    'app': model._meta.app_label,
                    'model': model._meta.model_name,
                    'field_path': self.field_path
                }
            )
            if request.GET:
                url = '%s?%s' % (url, request.GET.urlencode())
            self.fields[self.field_path] = forms.ChoiceField(
                choices=self.choices, required=False, widget=ListSelect2(url=url),
            )

        def field(self):
            return self[self.field_path]