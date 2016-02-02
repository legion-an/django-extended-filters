from django import forms
from django.utils.translation import ugettext as _
from django.contrib.admin.templatetags.admin_static import static
from django.contrib.admin.widgets import AdminDateWidget


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