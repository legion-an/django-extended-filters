from django.conf.urls import url

from .views import FilterListAutocomplete


urlpatterns = [
    url(r'^filter-list-autocomplete/(?P<app>\w+)-(?P<model>\w+)-(?P<field_path>\w+)/',
        FilterListAutocomplete.as_view(),
        name='filter_list_autocomplete')
]