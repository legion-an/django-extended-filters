from django.conf.urls import url

from .views import FilterListAutocomplete, FilterModelAutocomplete


urlpatterns = [
    url(r'^filter-list-autocomplete/(?P<app>\w+)-(?P<model>\w+)-(?P<field_path>\w+)/',
        FilterListAutocomplete.as_view(),
        name='filter_list_autocomplete'),
    url(r'^filter-model-autocomplete/(?P<app>\w+)-(?P<model>\w+)-(?P<field_path>\w+)/',
        FilterModelAutocomplete.as_view(),
        name='filter_model_autocomplete')
]