from django.urls import path

from . import views

app_name = 'enroll'
urlpatterns = [
    path('', views.indexView, name='index'),
]