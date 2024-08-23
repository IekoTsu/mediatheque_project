from django.urls import path
from . import views

urlpatterns = [
    path('', views.list_media, name='membre_list_media'),
]
