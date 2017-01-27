# add checkbox, date-range, tree-choice and autocomplete filters to django-admin
# create dropdown filter if choices count > 3

# Use DropDown filter: create templates/admin/filter.html 
# {% extends ‘extended_filters/filter.html’ %}


# Use filters in admin:
```
#!python

# admin.py
from extended_filters.filters import AutocompleteFilter, TreeDescendantsFilter, TreeDescendantsAutocompleteFilter, \
    DateRangeFilter, CheckBoxListFilter



class AdminModel(admin.Model):
    list_filter = [
        ('date', DateRangeFilter),   # date-range filter
        ('some_data', CheckBoxListFilter),   # checkbox
        ('category', TreeDescendantsFilter),    # filter your items in children category
        ('anouther_data', AutocompleteFilter),  # autocomplete
    ]

```
