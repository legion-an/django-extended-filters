add checkbox and date-range filters to django-admin create dropdown filter if choices count > 3

Use DropDown filter: create templates/admin/filter.html {% extends ‘extended_filters/filter.html’ %}

you can use checkbox and date-range filters with other in admin, regardless of the choice of filter order, query string not reset if you choose first default django filter and filter from lib

USE Checkbox and DateRange filters: in admin.py from extended_filters.filters import DateRangeFilter, CheckBoxListFilter

list_filters = [(‘date’, DateRangeFilter), (‘status’, CheckBoxListFilter)]