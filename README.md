# This package adds checkbox, date-range, tree-descendants and autocomplete filters to django-admin
date-range filter based on django-daterange-filter package https://pypi.python.org/pypi/django-daterange-filter

if you want to use autocomplete filter or tree-descendants filter you must install next packages:

for autocomplete:
```bash
pip install django-autocomplete-light
```

for tree filter:
```bash
pip install django-mptt
```

for DropDown filter you need to create templates/admin/filter.html with this code: 
```html
{% extends 'extended_filters/filter.html' %}
```
it creates dropdown filter only if choices count > 3

# Using filters:

admin.py
```python
from django.contrib import admin
from extended_filters.filters import AutocompleteFilter, TreeDescendantsFilter, TreeDescendantsAutocompleteFilter, \
    DateRangeFilter, CheckBoxListFilter

class AdminModel(admin.Model):
    list_filter = [
        ('date', DateRangeFilter),   # date-range filter
        ('some_data', CheckBoxListFilter),   # checkbox
        ('category', TreeDescendantsFilter),    # filter your items in children category
        ('another_data', AutocompleteFilter),  # autocomplete
    ]
    
    # if you want to use autocomplete filter please add static to your admin class
    class Media:
        css = AutocompleteFilter.Media.css
        js = AutocompleteFilter.Media.js

    # if you use autocomplete filter with related model, add fields that you want to use for filtering
    
    autocomplete_fields = {
        'category': ('title', 'text__icontains',)   # fields here are lookup key for queryset 
                                                    # so you can use anything of queryset methods (contains, startswith ...)
    }
    
```

urls.py
```python
# add to urls.py for autocomplete

urlpatterns = [
    ...
    url(r'^extended-filters/', include('extended_filters.urls')),
    ...
]

```

# TODO
1. make autocomplete filter using django autocomplete filter from version 2
