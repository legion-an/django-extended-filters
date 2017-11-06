# add checkbox, date-range, tree-descendants and autocomplete filters to django-admin
# date-range filter based on django-daterange-filter package https://pypi.python.org/pypi/django-daterange-filter/1.3.0


# if you want to use autocomplete filter or tree-descendants filter you must install next packages:
# autocomplete filter uses django-autocomplete-light package https://pypi.python.org/pypi/django-autocomplete-light
```
#!python
pip install django-autocomplete-light
```

# tree-descendants filter uses django-mptt package https://pypi.python.org/pypi/django-mptt
```
#!python
pip install django-mptt
```

# create dropdown filter if choices count > 3
# Using DropDown filter: create templates/admin/filter.html 
```
#!html
{% extends ‘extended_filters/filter.html’ %}
```

# Using filters:
# admin.py
```
#!python

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

# urls.py
```
#!python


# add to urls.py for autocomplete

urlpatterns = [
    ...
    url(r'^extended-filters/', include('extended_filters.urls')),
    ...
]

```
