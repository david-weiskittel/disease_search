from django.urls import path
from . import views

app_name = 'search_app'


urlpatterns = [
    path("", views.SearchView.as_view(), name="search"),
    path("get-conditions/", views.get_conditions, name="get_conditions"),
    path("get-conditions/XML/", views.get_conditions_brute_force, name="get_conditions_brute_force"),
]
